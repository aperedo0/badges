#include <metal_stdlib>
#include <RealityKit/RealityKit.h>
using namespace metal;

// The Diamond's gem look. RealityKit calls `badgeGemSurface` for every pixel
// of the gem; it traces the studio's light through the stone the way a game
// engine renders a diamond, so the flashes, the dark facets and the colored
// fringes all come from light, never from a picture on the model.
//
// What it is given (see `Badge3DGem` in BadgeHeroCard.swift):
//   - the gem's facet planes in the base color texture slot, one pixel per
//     plane: unit outward normal in red, green, blue and the offset in alpha
//     (`normal . x = offset` on the facet, `< offset` inside the gem);
//   - the studio's light, a full-strength equirectangular HDR map with
//     mipmaps, in the custom texture slot;
//   - custom parameter x = 1 for the mirror image under the floor.
//
// Per pixel: light reflects off the facet (Fresnel), and the rest refracts
// into the gem, bounces between its facets up to `kMaxInternalHits` times
// (total internal reflection, or partly out through a facet), and every part
// that leaves picks up the studio's light in its exit direction. The gem is
// convex, so a ray inside leaves through the first facet plane it reaches.

// ---- Tuning: every constant the look is judged by ----

// Index of refraction. Real diamond spreads red to blue by about 0.023; the
// spread is strengthened 1.5 times so colored fringes show at Home size.
constant float kIndexGreen = 2.423;
constant float kIndexRed = 2.4065;
constant float kIndexBlue = 2.4485;
// Facet hits one ray is followed through before the rest of it takes the
// light along its last direction.
constant int kMaxInternalHits = 5;
// Light lost per scene unit of path inside the stone, per color: red is
// absorbed fastest, so long paths turn the blue diamond's deep blue.
constant float3 kAbsorptionPerUnit = float3(0.34,0.16,0.03);
// The sharp light: the studio's map at this mip level, clamped so its tiny
// overhead spot cannot make pixel sized specks.
constant float kSharpMipLevel = 2.0;
constant float kSharpClamp = 12.0;
// The light tent: the same map, strongly blurred, so every direction gets
// some soft light and the gem is not mostly black between the flashes. The
// blur spreads the overhead spot's huge brightness over a wide patch of sky,
// so it is clamped too.
constant float kTentMipLevel = 7.0;
constant float kTentClamp = 3.0;
constant float kTentGain = 1.4;
// Brightness of the whole result.
constant float kExposure = 1.0;
// How far outside a facet plane a point may lie and still count as inside the
// gem: the planes reach this shader at half precision, which puts a point
// up to about 0.004 units outside a plane it truly lies inside.
constant float kPlaneRoundingTolerance = 0.004;

// ---- The studio's light ----

constexpr sampler kLightSampler(filter::linear, mip_filter::linear,
                                s_address::repeat, t_address::clamp_to_edge);

// Where a world direction lands on the equirectangular light map. RealityKit
// centers an environment map on -Z, and the stage is turned half a circle to
// face the map's lights, so the same convention holds here.
static float2 lightMapPosition(float3 direction)
{
    float u = 0.5 + atan2(direction.x, -direction.z) / (2.0 * M_PI_F);
    float v = 0.5 - asin(clamp(direction.y, -1.0, 1.0)) / M_PI_F;
    return float2(u, v);
}

struct StudioLight {
    texture2d<half> map;
    bool isMirrorImage;

    // The studio's own light along `direction` (world space), as a polished
    // surface would reflect it. The mirror image sees the studio flipped
    // through the floor.
    float3 sharp(float3 direction) const
    {
        if (isMirrorImage) direction.y = -direction.y;
        float2 position = lightMapPosition(direction);
        return min(float3(map.sample(kLightSampler, position, level(kSharpMipLevel)).rgb), kSharpClamp);
    }

    // The light that comes out of the gem along `direction`: the sharp light
    // plus the light tent.
    float3 along(float3 direction) const
    {
        if (isMirrorImage) direction.y = -direction.y;
        float2 position = lightMapPosition(direction);
        float3 tent = float3(map.sample(kLightSampler, position, level(kTentMipLevel)).rgb);
        return sharp(direction) + min(tent, kTentClamp) * kTentGain;
    }
};

// ---- Spaces ----

static float3 modelToWorldDirection(float3 direction, float4x4 modelToWorld)
{
    float3x3 rotationAndScale = float3x3(modelToWorld[0].xyz, modelToWorld[1].xyz, modelToWorld[2].xyz);
    return normalize(rotationAndScale * direction);
}

// The scale cancels in the normalize, so the transpose stands in for the
// inverse (the gem turns and scales uniformly).
static float3 worldToModelDirection(float3 direction, float4x4 modelToWorld)
{
    float3x3 rotationAndScale = float3x3(modelToWorld[0].xyz, modelToWorld[1].xyz, modelToWorld[2].xyz);
    return normalize(transpose(rotationAndScale) * direction);
}

// ---- Optics ----

// The share of unpolarized light a surface reflects, from the medium the
// light travels in into the other one; 1 when it cannot get through (total
// internal reflection).
static float fresnelReflectance(float cosIncident, float indexIncident, float indexTransmitted)
{
    float sinTransmittedSquared = (indexIncident / indexTransmitted) * (indexIncident / indexTransmitted)
                                  * (1.0 - cosIncident * cosIncident);
    if (sinTransmittedSquared >= 1.0) return 1.0;
    float cosTransmitted = sqrt(1.0 - sinTransmittedSquared);
    float perpendicular = (indexIncident * cosIncident - indexTransmitted * cosTransmitted)
                          / (indexIncident * cosIncident + indexTransmitted * cosTransmitted);
    float parallel = (indexIncident * cosTransmitted - indexTransmitted * cosIncident)
                     / (indexIncident * cosTransmitted + indexTransmitted * cosIncident);
    return 0.5 * (perpendicular * perpendicular + parallel * parallel);
}

struct FacetPlane {
    float3 normal;
    float offset;
};

static FacetPlane readPlane(texture2d<half> planes, uint index)
{
    float4 texel = float4(planes.read(uint2(index, 0)));
    return FacetPlane{texel.xyz, texel.w};
}

struct GemExit {
    bool found;
    float distance;
    float3 normal;
};

// The facet a ray at `position` going along `direction` leaves the gem
// through: the plane it reaches first. The tolerance is on the point's
// distance from the plane, never on the travelled distance, because dividing
// an error by a small `dot(normal, direction)` would skip a facet the ray is
// about to be totally reflected from.
static GemExit findExit(texture2d<half> planes, float3 position, float3 direction)
{
    GemExit nearest = GemExit{false, INFINITY, float3(0.0)};
    uint planeCount = planes.get_width();
    for (uint index = 0; index < planeCount; index++) {
        FacetPlane plane = readPlane(planes, index);
        float approach = dot(plane.normal, direction);
        if (approach <= 1e-4) continue;
        float gap = plane.offset - dot(plane.normal, position);
        if (gap <= -kPlaneRoundingTolerance) continue;
        float distance = max(gap, 0.0) / approach;
        if (distance < nearest.distance) nearest = GemExit{true, distance, plane.normal};
    }
    return nearest;
}

// The light a ray carrying `weight` brings out of the gem along three exit
// directions, one per color: each color bends by its own index of refraction
// as it leaves, which is the rainbow.
static float3 lightLeaving(StudioLight studio, float3 modelDirectionRed, float3 modelDirectionGreen,
                           float3 modelDirectionBlue, float4x4 modelToWorld)
{
    float red = studio.along(modelToWorldDirection(modelDirectionRed, modelToWorld)).r;
    float green = studio.along(modelToWorldDirection(modelDirectionGreen, modelToWorld)).g;
    float blue = studio.along(modelToWorldDirection(modelDirectionBlue, modelToWorld)).b;
    return float3(red, green, blue);
}

// Where a ray leaving through a facet goes, bent by `index`; if that color is
// totally reflected while green leaves, it follows green.
static float3 exitDirection(float3 direction, float3 outwardNormal, float index, float3 greenDirection)
{
    float3 bent = refract(direction, -outwardNormal, index);
    return all(bent == float3(0.0)) ? greenDirection : bent;
}

// The light the studio sends into the gem along the path that enters at
// `entryPoint` with the refracted `entryDirection` (model space).
static float3 lightThroughGem(texture2d<half> planes, StudioLight studio, float4x4 modelToWorld,
                              float3 entryPoint, float3 entryDirection, float3 entryWeight)
{
    float3 position = entryPoint;
    float3 direction = entryDirection;
    float3 weight = entryWeight;
    float3 collected = float3(0.0);
    for (int hit = 0; hit < kMaxInternalHits; hit++) {
        GemExit facet = findExit(planes, position, direction);
        if (!facet.found) break;
        position += direction * facet.distance;
        weight *= exp(-kAbsorptionPerUnit * facet.distance);

        float cosIncident = dot(facet.normal, direction);
        float reflected = fresnelReflectance(cosIncident, kIndexGreen, 1.0);
        if (reflected < 1.0) {
            float3 greenDirection = refract(direction, -facet.normal, kIndexGreen);
            float3 redDirection = exitDirection(direction, facet.normal, kIndexRed, greenDirection);
            float3 blueDirection = exitDirection(direction, facet.normal, kIndexBlue, greenDirection);
            collected += weight * (1.0 - reflected)
                       * lightLeaving(studio, redDirection, greenDirection, blueDirection, modelToWorld);
        }
        weight *= reflected;
        direction = reflect(direction, facet.normal);
    }
    // A ray that ran out of hits, or was found outside the gem (a pixel at the
    // silhouette), takes the light along its last direction.
    float3 lastDirection = modelToWorldDirection(direction, modelToWorld);
    return collected + weight * studio.along(lastDirection);
}

// ---- The surface shader ----

[[visible]]
void badgeGemSurface(realitykit::surface_parameters params)
{
    realitykit::surface::surface_properties surface = params.surface();
    float4x4 modelToWorld = params.uniforms().model_to_world();
    StudioLight studio = StudioLight{params.textures().custom(), params.uniforms().custom_parameter().x > 0.5};
    texture2d<half> planes = params.textures().base_color();

    // Which way the camera's ray travels, in model space.
    float3 incident = -worldToModelDirection(params.geometry().view_direction(), modelToWorld);
    float3 facetNormal = worldToModelDirection(params.geometry().normal(), modelToWorld);
    // Face the camera, so a pixel at the silhouette never shades from behind.
    if (dot(facetNormal, incident) > 0.0) facetNormal = -facetNormal;

    float cosEntry = dot(facetNormal, -incident);
    float surfaceReflection = fresnelReflectance(cosEntry, 1.0, kIndexGreen);
    float3 mirrored = modelToWorldDirection(reflect(incident, facetNormal), modelToWorld);
    float3 refractedDirection = refract(incident, facetNormal, 1.0 / kIndexGreen);
    float3 throughGem = lightThroughGem(planes, studio, modelToWorld, params.geometry().model_position(),
                                        refractedDirection, float3(1.0 - surfaceReflection));
    float3 color = surfaceReflection * studio.sharp(mirrored) + throughGem;

    surface.set_emissive_color(half3(color * kExposure));
    surface.set_opacity(1.0h);
}

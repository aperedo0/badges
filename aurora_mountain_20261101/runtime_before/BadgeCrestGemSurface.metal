// Crest ice, sapphire and ruby optics. The approved Diamond shader stays separate.
#include <metal_stdlib>
#include <RealityKit/RealityKit.h>
using namespace metal;

// Ice, sapphire and ruby use independent closed convex stones. Each pixel
// traces the fixed studio environment through the current facet directions.
// custom_parameter: x mirror flag, y stone profile, z optical density, w exposure.
// Paired half precision rows preserve the plane data; no appearance picture is sampled on a gem.
// Three outer facet hits keep motion continuous at the preview's mobile size.
constant int cMaxInternalHits = 3;
// Light lost per scene unit of path inside the stone, per color: red is
// absorbed fastest, so long paths turn the blue diamond's deep blue.
// The sharp light: the studio's map at this mip level, clamped so its tiny
// overhead spot cannot make pixel sized specks. Surface reflections use only
// this light, like a polished surface does.
constant float cSharpMipLevel = 1.0;
constant float cSharpClamp = 24.0;
// The light tent, added to the light that comes out of the gem: the same map,
// strongly blurred, so every direction gets some soft light and the gem is not
// mostly black between the flashes. The blur spreads the overhead spot's huge
// brightness over a wide patch of sky, so the tent is clamped too.
constant float cTentMipLevel = 8.0;
constant float cTentClamp = 3.0;
constant float cTentGain = 3.0;
// Tolerance for full precision facet planes and exported float vertices.
constant float cPlaneRoundingTolerance = 0.00001;

// ---- The studio's light ----

constexpr sampler cLightSampler(filter::linear, mip_filter::linear,
                                s_address::repeat, t_address::clamp_to_edge);

// Where a world direction lands on the equirectangular light map: RealityKit's
// own convention for an environment map, which centers it on -Z (the stage is
// turned half a circle so the studio's lights face the camera). A mirror
// sphere lit by this lookup and by RealityKit's own environment lighting
// showed the same softboxes in the same places at the same brightness.
static float2 crestLightMapPosition(float3 direction)
{
    float u = 0.5 + atan2(direction.x, -direction.z) / (2.0 * M_PI_F);
    float v = 0.5 - asin(clamp(direction.y, -1.0, 1.0)) / M_PI_F;
    return float2(u, v);
}

struct crestStudioLight {
    texture2d<half> map;
    bool isMirrorImage;

    // Where `direction` (world space) looks into the light map. The mirror
    // image sees the studio flipped through the floor, so it looks the other
    // way up. Every lookup starts here, so the flip happens exactly once.
    float2 mapPosition(float3 direction) const
    {
        if (isMirrorImage) direction.y = -direction.y;
        return crestLightMapPosition(direction);
    }

    // The studio's own light along `direction`, as a polished surface would
    // reflect it.
    float3 sharp(float3 direction) const
    {
        return sharpAt(mapPosition(direction));
    }

    // The light that comes out of the gem along `direction`: the sharp light
    // plus the light tent.
    float3 along(float3 direction) const
    {
        float2 position = mapPosition(direction);
        float3 tent = float3(map.sample(cLightSampler, position, level(cTentMipLevel)).rgb);
        return sharpAt(position) + min(tent, cTentClamp) * cTentGain;
    }

    // The sharp light at a position in the map, which is already flipped for
    // the mirror image.
    float3 sharpAt(float2 position) const
    {
        return min(float3(map.sample(cLightSampler, position, level(cSharpMipLevel)).rgb), cSharpClamp);
    }
};

// ---- Spaces ----

static float3 crestModelToWorldDirection(float3 direction, float4x4 modelToWorld)
{
    float3x3 rotationAndScale = float3x3(modelToWorld[0].xyz, modelToWorld[1].xyz, modelToWorld[2].xyz);
    return normalize(rotationAndScale * direction);
}

// The scale cancels in the normalize, so the transpose stands in for the
// inverse (the gem turns and scales uniformly).
static float3 crestWorldToModelDirection(float3 direction, float4x4 modelToWorld)
{
    float3x3 rotationAndScale = float3x3(modelToWorld[0].xyz, modelToWorld[1].xyz, modelToWorld[2].xyz);
    return normalize(transpose(rotationAndScale) * direction);
}

// ---- Optics ----

// The share of unpolarized light a surface reflects, from the medium the
// light travels in into the other one; 1 when it cannot get through (total
// internal reflection).
static float crestFresnelReflectance(float cosIncident, float indexIncident, float indexTransmitted)
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

struct crestFacetPlane {
    float3 normal;
    float offset;
};

static crestFacetPlane crestReadPlane(texture2d<half> planes, uint index)
{
    float4 texel = float4(planes.read(uint2(index, 0)));
    if (planes.get_height() > 1) texel += float4(planes.read(uint2(index, 1))) / 1024.0;
    return crestFacetPlane{texel.xyz, texel.w};
}

struct crestGemExit {
    bool found;
    float distance;
    float3 normal;
};

// The facet a ray at `position` going along `direction` leaves the gem
// through: the plane it reaches first. The tolerance is on the point's
// distance from the plane, never on the travelled distance, because dividing
// an error by a small `dot(normal, direction)` would skip a facet the ray is
// about to be totally reflected from.
static crestGemExit crestFindExit(texture2d<half> planes, float3 position, float3 direction)
{
    crestGemExit nearest = crestGemExit{false, INFINITY, float3(0.0)};
    uint planeCount = planes.get_width();
    for (uint index = 0; index < planeCount; index++) {
        crestFacetPlane plane = crestReadPlane(planes, index);
        float approach = dot(plane.normal, direction);
        if (approach <= 1e-4) continue;
        float gap = plane.offset - dot(plane.normal, position);
        if (gap <= -cPlaneRoundingTolerance) continue;
        float distance = max(gap, 0.0) / approach;
        if (distance < nearest.distance) nearest = crestGemExit{true, distance, plane.normal};
    }
    return nearest;
}

// The light that comes out of the gem along three exit directions, one per
// color: each color bends by its own index of refraction as it leaves, which
// is the rainbow.
static float3 crestLightLeaving(crestStudioLight studio, float3 modelDirectionRed, float3 modelDirectionGreen,
                           float3 modelDirectionBlue, float4x4 modelToWorld)
{
    float red = studio.along(crestModelToWorldDirection(modelDirectionRed, modelToWorld)).r;
    float green = studio.along(crestModelToWorldDirection(modelDirectionGreen, modelToWorld)).g;
    float blue = studio.along(crestModelToWorldDirection(modelDirectionBlue, modelToWorld)).b;
    return float3(red, green, blue);
}

// Where a ray leaving through a facet goes, bent by `index`; if that color is
// totally reflected while green leaves, it follows green.
static float3 crestExitDirection(float3 direction, float3 outwardNormal, float index, float3 greenDirection)
{
    float3 bent = refract(direction, -outwardNormal, index);
    return all(bent == float3(0.0)) ? greenDirection : bent;
}

// Intrinsic inclusions occupy the stone's model space. Rays sample this
// volume along their refracted paths, so the interior changes with view angle.
static float crestHash(float3 p) {
    return fract(sin(dot(p, float3(127.1, 311.7, 74.7))) * 43758.5453);
}
static float crestNoise(float3 p) {
    float3 a = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f);
    float x00 = mix(crestHash(a), crestHash(a + float3(1,0,0)), f.x);
    float x10 = mix(crestHash(a + float3(0,1,0)), crestHash(a + float3(1,1,0)), f.x);
    float x01 = mix(crestHash(a + float3(0,0,1)), crestHash(a + float3(1,0,1)), f.x);
    float x11 = mix(crestHash(a + float3(0,1,1)), crestHash(a + float3(1,1,1)), f.x);
    return mix(mix(x00, x10, f.y), mix(x01, x11, f.y), f.z);
}
static float crestOpticalDensity(float3 p) {
    float cloud = crestNoise(p * float3(10, 7, 12));
    float detail = crestNoise(p * float3(23, 17, 19));
    return 0.28 + cloud * cloud * 2.5 + detail * 0.4;
}

// The light the studio sends into the gem along the path that enters at
// `entryPoint` with the refracted `entryDirection` (model space).
static float3 crestLightThroughGem(texture2d<half> planes, crestStudioLight studio, float4x4 modelToWorld,
                              float3 entryPoint, float3 entryDirection, float3 entryWeight, float3 indices, float3 absorption, bool ice)
{
    float3 position = entryPoint;
    float3 direction = entryDirection;
    float3 weight = entryWeight;
    float3 collected = float3(0.0);
    for (int hit = 0; hit < cMaxInternalHits; hit++) {
        crestGemExit facet = crestFindExit(planes, position, direction);
        if (!facet.found) break;
        float density = 0.0;
        for (int step = 0; step < 4; step++) {
            float3 samplePosition = position + direction * facet.distance * (float(step) + 0.5) / 4.0;
            if (studio.isMirrorImage) samplePosition.y = -samplePosition.y;
            density += crestOpticalDensity(samplePosition);
        }
        // Thin internal cleavage surfaces reflect actual studio light. Their
        // bounded planes stay inside the crystal and never alter its silhouette.
        if (ice) {
            float3 lastCell = float3(INFINITY);
            for (int sample = 0; sample < 6; sample++) {
                float3 probe = position + direction * facet.distance * (float(sample) + 0.5) / 6.0;
                if (studio.isMirrorImage) probe.y = -probe.y;
                float cellSize = 0.28;
                float3 cell = floor(probe / cellSize);
                if (all(cell == lastCell)) continue;
                lastCell = cell;
                float3 center = (cell + 0.5) * cellSize;
                float3 normal = normalize(float3(crestHash(cell), crestHash(cell + 13.0), crestHash(cell + 29.0)) * 2.0 - 1.0);
                if (studio.isMirrorImage) { center.y = -center.y; normal.y = -normal.y; }
                float approach = dot(direction, normal);
                if (abs(approach) < 0.001) continue;
                float distance = dot(center - position, normal) / approach;
                float3 hitPoint = position + direction * distance;
                if (distance <= 0.001 || distance >= facet.distance || any(abs(hitPoint - center) > cellSize * 0.5)) continue;
                if (approach > 0.0) normal = -normal;
                float share = 0.10 * crestFresnelReflectance(abs(approach), indices.y, 1.0);
                float3 secondaryPosition = hitPoint;
                float3 secondaryDirection = reflect(direction, normal);
                float3 secondaryWeight = weight * share * exp(-absorption * distance);
                for (int bounce = 0; bounce < 2; bounce++) {
                    crestGemExit exit = crestFindExit(planes, secondaryPosition, secondaryDirection);
                    if (!exit.found) break;
                    secondaryPosition += secondaryDirection * exit.distance;
                    secondaryWeight *= exp(-absorption * exit.distance);
                    float reflection = crestFresnelReflectance(dot(exit.normal, secondaryDirection), indices.y, 1.0);
                    if (reflection < 1.0) {
                        float3 outside = refract(secondaryDirection, -exit.normal, indices.y);
                        collected += secondaryWeight * (1.0 - reflection) * studio.along(crestModelToWorldDirection(outside, modelToWorld));
                    }
                    secondaryWeight *= reflection;
                    secondaryDirection = reflect(secondaryDirection, exit.normal);
                }
                weight *= 1.0 - share;
                break;
            }
        }
        position += direction * facet.distance;
        weight *= exp(-absorption * facet.distance * density / 4.0);

        float cosIncident = dot(facet.normal, direction);
        float reflected = crestFresnelReflectance(cosIncident, indices.y, 1.0);
        if (reflected < 1.0) {
            float3 greenDirection = refract(direction, -facet.normal, indices.y);
            float3 redDirection = crestExitDirection(direction, facet.normal, indices.x, greenDirection);
            float3 blueDirection = crestExitDirection(direction, facet.normal, indices.z, greenDirection);
            collected += weight * (1.0 - reflected)
                       * crestLightLeaving(studio, redDirection, greenDirection, blueDirection, modelToWorld);
        }
        weight *= reflected;
        direction = reflect(direction, facet.normal);
    }
    // A ray that ran out of hits, or was found outside the gem (a pixel at the
    // silhouette), takes the light along its last direction.
    float3 lastDirection = crestModelToWorldDirection(direction, modelToWorld);
    return collected + weight * studio.along(lastDirection);
}

// ---- The surface shader ----

[[visible]]
void badgeCrestGemSurface(realitykit::surface_parameters params)
{
    float4 profile = params.uniforms().custom_parameter();
    float3 indices = profile.y < 0.5 ? float3(1.45, 1.46, 1.475) : float3(1.76, 1.77, 1.79);
    float3 absorption = profile.y < 0.5 ? float3(0.50, 0.20, 0.04)
                        : profile.y < 1.5 ? float3(8.0, 4.0, 0.25) : float3(1.25, 16.0, 12.0);
    absorption *= profile.z;

    realitykit::surface::surface_properties surface = params.surface();
    float4x4 modelToWorld = params.uniforms().model_to_world();
    crestStudioLight studio = crestStudioLight{params.textures().custom(), params.uniforms().custom_parameter().x > 0.5};
    texture2d<half> planes = params.textures().base_color();

    // Which way the camera's ray travels, in model space.
    float3 incident = -crestWorldToModelDirection(params.geometry().view_direction(), modelToWorld);
    float3 facetNormal = crestWorldToModelDirection(params.geometry().normal(), modelToWorld);
    // Face the camera, so a pixel at the silhouette never shades from behind.
    if (dot(facetNormal, incident) > 0.0) facetNormal = -facetNormal;

    float cosEntry = dot(facetNormal, -incident);
    float surfaceReflection = crestFresnelReflectance(cosEntry, 1.0, indices.y);
    float3 mirrored = crestModelToWorldDirection(reflect(incident, facetNormal), modelToWorld);
    float3 refractedDirection = refract(incident, facetNormal, 1.0 / indices.y);
    float3 throughGem = crestLightThroughGem(planes, studio, modelToWorld, params.geometry().model_position(),
                                        refractedDirection, float3(1.0 - surfaceReflection), indices, absorption, profile.y < 0.5);
    float3 color = surfaceReflection * studio.sharp(mirrored) + throughGem;

    surface.set_emissive_color(half3(color * profile.w));
    surface.set_opacity(1.0h);
}

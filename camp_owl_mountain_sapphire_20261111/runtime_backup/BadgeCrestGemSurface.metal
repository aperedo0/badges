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
    float softTentGain;

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
        return sharpAt(position) + min(tent, cTentClamp) * softTentGain;
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

// The heart is the geometric union of two convex lobe domains. A ray
// crosses their common face inside the same ruby, without refraction there.
struct crestHullInterval {
    bool found;
    bool contains;
    float entry;
    float exit;
    float3 normal;
};

static crestHullInterval crestHeartInterval(texture2d<half> planes, uint domain,
                                            float3 position, float3 direction)
{
    float4 metadata = float4(planes.read(uint2(0, 4)));
    uint count = min(256u, uint(round(metadata[domain])));
    float first = -INFINITY, last = INFINITY;
    float3 normal = float3(0);
    bool contains = true;
    for (uint index = 0; index < count; index++) {
        float4 p = float4(planes.read(uint2(index, domain * 2)))
                 + float4(planes.read(uint2(index, domain * 2 + 1))) / 1024.0;
        float rawGap = p.w - dot(p.xyz, position);
        contains = contains && rawGap >= -cPlaneRoundingTolerance;
        float gap = abs(rawGap) <= cPlaneRoundingTolerance ? 0.0 : rawGap;
        float approach = dot(p.xyz, direction);
        if (abs(approach) < 1e-6) {
            if (gap < -cPlaneRoundingTolerance) return crestHullInterval{false, false, 0, 0, float3(0)};
            continue;
        }
        float distance = gap / approach;
        if (approach > 0.0) {
            if (distance < last) { last = distance; normal = p.xyz; }
        } else {
            first = max(first, distance);
        }
    }
    bool hit = count >= 4 && last >= -cPlaneRoundingTolerance
              && first <= last + cPlaneRoundingTolerance;
    return crestHullInterval{hit, contains, first, max(last, 0.0), normal};
}

static crestGemExit crestFindHeartExit(texture2d<half> planes, float3 position, float3 direction)
{
    crestHullInterval a = crestHeartInterval(planes, 0, position, direction);
    crestHullInterval b = crestHeartInterval(planes, 1, position, direction);
    // At partially covered facet pixels the interpolated position can sit
    // just outside the volume. Start with the first forward intersection,
    // so multisample edge coverage never becomes an unattenuated white line.
    if (!a.found && !b.found) return crestGemExit{false, INFINITY, float3(0)};
    bool startA = a.found && (!b.found || max(a.entry, 0.0) <= max(b.entry, 0.0));
    crestHullInterval current = startA ? a : b;
    crestHullInterval other = startA ? b : a;
    if (other.found && other.entry <= current.exit + 2.0 * cPlaneRoundingTolerance
                    && other.exit > current.exit) current = other;
    return crestGemExit{true, current.exit, current.normal};
}

// The facet a ray at `position` going along `direction` leaves the gem
// through: the plane it reaches first. The tolerance is on the point's
// distance from the plane, never on the travelled distance, because dividing
// an error by a small `dot(normal, direction)` would skip a facet the ray is
// about to be totally reflected from.
static crestGemExit crestFindExit(texture2d<half> planes, float3 position, float3 direction)
{
    if (planes.get_height() > 2) return crestFindHeartExit(planes, position, direction);
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
                              float3 entryPoint, float3 entryDirection, float3 entryWeight, float3 indices, float3 absorption, bool ice, bool clearStone)
{
    float3 position = entryPoint;
    float3 direction = entryDirection;
    float3 weight = entryWeight;
    float3 collected = float3(0.0);
    bool rose = planes.get_height() > 2;
    int hitBudget = rose ? 6 : cMaxInternalHits;
    for (int hit = 0; hit < hitBudget; hit++) {
        crestGemExit facet = crestFindExit(planes, position, direction);
        if (!facet.found) break;
        float density = 0.0;
        for (int step = 0; step < 4; step++) {
            float3 samplePosition = position + direction * facet.distance * (float(step) + 0.5) / 4.0;
            if (studio.isMirrorImage) samplePosition.y = -samplePosition.y;
            density += clearStone ? 0.96 + 0.06 * crestNoise(samplePosition * 3.0) : crestOpticalDensity(samplePosition);
        }
        // Thin internal cleavage surfaces reflect actual studio light. Their
        // bounded planes stay inside the crystal and never alter its silhouette.
        if (ice || (rose && hit == 0)) {
            float3 lastCell = float3(INFINITY);
            for (int sample = 0; sample < 6; sample++) {
                float3 probe = position + direction * facet.distance * (float(sample) + 0.5) / 6.0;
                if (studio.isMirrorImage) probe.y = -probe.y;
                float cellSize = rose ? 0.16 : 0.28;
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
                float share = (rose ? 0.065 : 0.10) * crestFresnelReflectance(abs(approach), indices.y, 1.0);
                float3 secondaryPosition = hitPoint;
                float3 secondaryDirection = reflect(direction, normal);
                float3 secondaryWeight = weight * share * exp(-absorption * distance);
                for (int bounce = 0; bounce < (rose ? 1 : 2); bounce++) {
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

// ---- Ruby Heart: a thin faceted ruby on a mirror foil (profile 10) ----
// The stone's front and back crowns meet a mirror foil at model z = 0, like a
// closed back jewelry setting. Light enters a facet, refracts, is absorbed on
// its way to the foil and back, and leaves through the same facet plane, so
// each facet shows one direction of the studio and keeps its ruby color while
// turning. No plane data or picture is read; the facet normal is the mesh's.
constant float cHeartIor = 1.77;
constant float3 cHeartAbsorption = float3(0.150000, 6.500000, 2.200000);
constant float cHeartFoil = 0.920000;
constant float cHeartBodyLevel = 2.146406;
constant float cHeartBodyClamp = 0.700000;
constant float cHeartSpecClamp = 10.000000;
// The stone continues below its visible top, so thin edges still read red.
constant float cHeartPathBase = 0.000000;
constant float cHeartSpecFloor = 3.000000;
constant float cHeartSpecGain = 1.810354;
constant float cHeartTentGain = 0.260400;
constant float3 cHeartGlow = float3(0.160000, 0.003200, 0.024000);

static float3 crestHeartLight(crestStudioLight studio, float3 modelDirection, float4x4 modelToWorld)
{
    float2 position = studio.mapPosition(crestModelToWorldDirection(modelDirection, modelToWorld));
    float3 body = min(float3(studio.map.sample(cLightSampler, position, level(cHeartBodyLevel)).rgb), cHeartBodyClamp);
    float3 tent = min(float3(studio.map.sample(cLightSampler, position, level(cTentMipLevel)).rgb), cTentClamp);
    return body + tent * cHeartTentGain;
}

static float3 crestHeartFoil(crestStudioLight studio, float4x4 modelToWorld, float3 entry,
                             float3 incident, float3 normal)
{
    float cosEntry = clamp(dot(normal, -incident), 0.0, 1.0);
    float surfaceReflection = crestFresnelReflectance(cosEntry, 1.0, cHeartIor);
    float3 mirrored = crestModelToWorldDirection(reflect(incident, normal), modelToWorld);
    // Only the studio's bright lights leave a white glint; the dim fill behind
    // the camera (radiance 1.4) would otherwise lay a pale veil over the red.
    float3 color = cHeartSpecGain * surfaceReflection * clamp(studio.sharp(mirrored) - cHeartSpecFloor, 0.0, cHeartSpecClamp);
    float side = entry.z >= 0.0 ? 1.0 : -1.0;
    float3 position = entry;
    float3 direction = refract(incident, normal, 1.0 / cHeartIor);
    float3 weight = float3(1.0 - surfaceReflection);
    float path = 0.0;
    for (int bounce = 0; bounce < 4; bounce++) {
        float toFoil = direction.z * side < -1e-4 ? max(-position.z / direction.z, 0.0) : 0.0;
        position += direction * toFoil;
        path += toFoil;
        direction.z = -direction.z;
        weight *= cHeartFoil;
        float approach = dot(normal, direction);
        float back = approach > 1e-4 ? max(dot(normal, entry - position) / approach, 0.0) : 0.0;
        position += direction * back;
        path += back;
        float internal = crestFresnelReflectance(clamp(approach, 0.0, 1.0), cHeartIor, 1.0);
        // Paths are never negative, so absorption can only darken.
        float3 transmitted = exp(-cHeartAbsorption * (min(path, 12.0) + cHeartPathBase));
        if (internal < 1.0) {
            float3 leaving = refract(direction, -normal, cHeartIor);
            color += weight * transmitted * (1.0 - internal) * crestHeartLight(studio, leaving, modelToWorld);
        }
        weight *= internal;
        direction = reflect(direction, normal);
    }
    float3 tent = min(float3(studio.map.sample(cLightSampler,
                      studio.mapPosition(crestModelToWorldDirection(direction, modelToWorld)), level(cTentMipLevel)).rgb), cTentClamp);
    color += weight * exp(-cHeartAbsorption * (min(path, 12.0) + cHeartPathBase)) * tent * cHeartTentGain;
    return color + (1.0 - surfaceReflection) * cHeartGlow;
}

// Crown rubies: deep crimson with a dark wine core (the heart's ruby is lighter).
constant float3 cCrownRubyAbsorption = float3(0.30, 7.0, 2.4);
constant float cCrownSpecGain = 0.5;
constant float3 cCrownRubyGlow = float3(0.06, 0.0, 0.006);

// ---- Ruby Crown stones: the heart's foil optics with a per stone backing (profiles 12, 13) ----
// Each stone's foil faces along its own axis, stored in the mesh's first UV set as
// (azimuth / 2 pi, elevation / pi + 0.5), azimuth from +Z toward +X. custom z is the
// stone's nominal depth above its foil. 12 is ruby, 13 is a clear white stone.
// Emerald Stag stones (profile 15): green passes, red is absorbed fastest.
constant float3 cEmeraldAbsorption = float3(5.0, 0.35, 2.6);
constant float3 cEmeraldGlow = float3(0.004, 0.05, 0.022);

static float3 crestCrownFoil(crestStudioLight studio, float4x4 modelToWorld, float3 entry, float3 incident,
                             float3 normal, float3 axis, float depth, float3 absorption, float3 glow)
{
    float cosEntry = clamp(dot(normal, -incident), 0.0, 1.0);
    float surfaceReflection = crestFresnelReflectance(cosEntry, 1.0, cHeartIor);
    float3 mirrored = crestModelToWorldDirection(reflect(incident, normal), modelToWorld);
    float3 color = cCrownSpecGain * surfaceReflection * clamp(studio.sharp(mirrored) - cHeartSpecFloor, 0.0, cHeartSpecClamp);
    float foilOffset = dot(axis, entry) - depth;
    float3 position = entry;
    float3 direction = refract(incident, normal, 1.0 / cHeartIor);
    float3 weight = float3(1.0 - surfaceReflection);
    float path = 0.0;
    for (int bounce = 0; bounce < 4; bounce++) {
        float along = dot(direction, axis);
        float toFoil = along < -1e-4 ? max((dot(axis, position) - foilOffset) / -along, 0.0) : 0.0;
        position += direction * toFoil;
        path += toFoil;
        direction -= 2.0 * dot(direction, axis) * axis;
        weight *= cHeartFoil;
        float approach = dot(normal, direction);
        float back = approach > 1e-4 ? max(dot(normal, entry - position) / approach, 0.0) : 0.0;
        position += direction * back;
        path += back;
        float internal = crestFresnelReflectance(clamp(approach, 0.0, 1.0), cHeartIor, 1.0);
        float3 transmitted = exp(-absorption * min(path, 12.0));
        if (internal < 1.0) {
            float3 leaving = refract(direction, -normal, cHeartIor);
            color += weight * transmitted * (1.0 - internal) * crestHeartLight(studio, leaving, modelToWorld);
        }
        weight *= internal;
        direction = reflect(direction, normal);
    }
    float3 tent = min(float3(studio.map.sample(cLightSampler,
                      studio.mapPosition(crestModelToWorldDirection(direction, modelToWorld)), level(cTentMipLevel)).rgb), cTentClamp);
    color += weight * exp(-absorption * min(path, 12.0)) * tent * cHeartTentGain;
    return color + (1.0 - surfaceReflection) * glow;
}

// ---- The surface shader ----

[[visible]]
void badgeCrestGemSurface(realitykit::surface_parameters params)
{
    float4 profile = params.uniforms().custom_parameter();
    // Blue Hourglass glass (profile 16): colorless, see through; Fresnel reflections of the studio,
    // softened so the small lights never become pin dots, and a bright rim where the glass turns away.
    if (profile.y > 15.5 && profile.y < 16.5) {
        realitykit::surface::surface_properties glass = params.surface();
        float4x4 glassToWorld = params.uniforms().model_to_world();
        crestStudioLight glassStudio = crestStudioLight{params.textures().custom(), profile.x > 0.5, 0.0};
        float3 glassIncident = -crestWorldToModelDirection(params.geometry().view_direction(), glassToWorld);
        float3 glassNormal = crestWorldToModelDirection(params.geometry().normal(), glassToWorld);
        if (dot(glassNormal, glassIncident) > 0.0) glassNormal = -glassNormal;
        float facing = clamp(dot(glassNormal, -glassIncident), 0.0, 1.0);
        float fresnel = 0.04 + 0.96 * pow(1.0 - facing, 5.0);
        float2 mapPos = glassStudio.mapPosition(crestModelToWorldDirection(reflect(glassIncident, glassNormal), glassToWorld));
        // Only the studio's bright lights reflect, as crisp curved streaks; the dim fill stays clear (no haze).
        float3 lights = max(float3(glassStudio.map.sample(cLightSampler, mapPos, level(2.0)).rgb) - 1.6, 0.0);
        // Light reflections grow toward the walls (where the glass turns away), so they read as curved streaks
        // along the walls instead of flat squares floating in the middle of the bulbs.
        float wallness = smoothstep(0.30, 0.80, 1.0 - facing);
        // Steeply tilted glass (just below the neck) would mirror the overhead spot as a white bar; keep it clear.
        wallness *= 1.0 - smoothstep(0.45, 0.80, abs(glassNormal.y));
        float edge = pow(1.0 - facing, 5.0);   // a thin bright outline only where the glass turns fully away
        float3 glassColor = min(lights * (0.03 + 1.8 * fresnel) * wallness * 1.4, 3.0) + float3(0.85 * edge);
        float glassLum = dot(glassColor, float3(0.2126, 0.7152, 0.0722));
        float glassOpacity = clamp(0.01 + 0.75 * edge + 0.45 * glassLum, 0.0, 0.90);
        glass.set_emissive_color(half3(glassColor * profile.w));
        glass.set_opacity(half(glassOpacity));
        return;
    }
    if ((profile.y > 11.5 && profile.y < 15.5) || (profile.y > 16.5 && profile.y < 17.5)) {
        realitykit::surface::surface_properties stone = params.surface();
        float4x4 stoneToWorld = params.uniforms().model_to_world();
        bool mirror = profile.x > 0.5;
        crestStudioLight stoneStudio = crestStudioLight{params.textures().custom(), mirror, 0.0};
        float3 stoneIncident = -crestWorldToModelDirection(params.geometry().view_direction(), stoneToWorld);
        float3 stoneNormal = crestWorldToModelDirection(params.geometry().normal(), stoneToWorld);
        if (dot(stoneNormal, stoneIncident) > 0.0) stoneNormal = -stoneNormal;
        float2 code = float2(params.geometry().uv0());
        float azimuth = code.x * 2.0 * M_PI_F;
        float elevation = (code.y - 0.5) * M_PI_F;
        float3 axis = float3(cos(elevation) * sin(azimuth), sin(elevation), cos(elevation) * cos(azimuth));
        if (mirror) axis.y = -axis.y;
        axis = normalize(axis);
        bool sapphire = profile.y > 16.5;
        bool emerald = profile.y > 14.5 && !sapphire;
        bool ruby = !emerald && !sapphire && (profile.y < 12.5 || profile.y > 13.5);
        float3 absorption = sapphire ? float3(3.2, 0.7, 0.18) : emerald ? cEmeraldAbsorption : ruby ? cCrownRubyAbsorption : float3(0.03, 0.03, 0.02);
        float3 glow = sapphire ? float3(0.004, 0.03, 0.07) : emerald ? cEmeraldGlow : ruby ? cCrownRubyGlow : float3(0.0);
        float3 stoneColor = crestCrownFoil(stoneStudio, stoneToWorld, params.geometry().model_position(),
                                           stoneIncident, stoneNormal, axis, profile.z, absorption, glow);
        stone.set_emissive_color(half3(stoneColor * profile.w));
        stone.set_opacity(1.0h);
        return;
    }
    if (profile.y > 9.5 && profile.y < 10.5) {
        realitykit::surface::surface_properties heart = params.surface();
        float4x4 heartToWorld = params.uniforms().model_to_world();
        crestStudioLight heartStudio = crestStudioLight{params.textures().custom(), profile.x > 0.5, 0.0};
        float3 heartIncident = -crestWorldToModelDirection(params.geometry().view_direction(), heartToWorld);
        float3 heartNormal = crestWorldToModelDirection(params.geometry().normal(), heartToWorld);
        if (dot(heartNormal, heartIncident) > 0.0) heartNormal = -heartNormal;
        float3 heartColor = crestHeartFoil(heartStudio, heartToWorld, params.geometry().model_position(),
                                           heartIncident, heartNormal);
        heart.set_emissive_color(half3(heartColor * profile.w));
        heart.set_opacity(1.0h);
        return;
    }
    float3 indices = ((profile.y > 4.5 && profile.y < 5.5) || (profile.y > 7.5 && profile.y < 8.5)) ? float3(1.57, 1.58, 1.59)
                   : profile.y < 0.5 ? float3(1.45, 1.46, 1.475)
                   : profile.y > 2.5 && profile.y < 3.5 ? float3(1.54, 1.55, 1.56) : float3(1.76, 1.77, 1.79);
    // Astral's sapphires absorb more light through their real internal paths.
    // Existing crest profiles retain their original optical constants.
    float3 absorption = profile.y > 8.5 ? float3(0.45, 9.0, 7.0)
                        : profile.y > 7.5 ? float3(0.45, 0.16, 0.05)
                        : profile.y > 6.5 ? float3(10.0, 6.0, 1.6)
                        : profile.y > 5.5 ? float3(0.042528659, 9.0, 0.721236937)
                        : profile.y > 4.5 ? float3(16.0, 2.8, 6.2)
                        : profile.y > 3.5 ? float3(10.0, 6.0, 1.6)
                        : profile.y < 0.5 ? float3(0.50, 0.20, 0.04)
                        : profile.y < 1.5 ? float3(8.0, 4.0, 0.25)
                        : profile.y > 2.5 ? float3(0.90, 12.0, 0.50) : float3(1.25, 16.0, 12.0);
    absorption *= profile.z;

    realitykit::surface::surface_properties surface = params.surface();
    float4x4 modelToWorld = params.uniforms().model_to_world();
    float softTentGain = profile.y > 8.5 && profile.y < 9.5 ? 1.2
                       : profile.y > 5.5 && profile.y < 6.5 ? 0.9
                       : profile.y > 2.5 && profile.y < 3.5 ? 1.2
                       : profile.y > 7.5 && profile.y < 8.5 ? 1.2 : cTentGain;
    crestStudioLight studio = crestStudioLight{params.textures().custom(), params.uniforms().custom_parameter().x > 0.5, softTentGain};
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
                                        refractedDirection, float3(1.0 - surfaceReflection), indices, absorption, profile.y < 0.5, profile.y > 4.5 || (profile.y > 2.5 && profile.y < 3.5));
    float3 color = surfaceReflection * studio.sharp(mirrored) + throughGem;

    surface.set_emissive_color(half3(color * profile.w));
    surface.set_opacity(1.0h);
}

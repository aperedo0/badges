"""Create a reviewable Diamond-only image-space optical streak candidate."""
from pathlib import Path
import sys, shutil
ROOT=Path(__file__).resolve().parents[1]
base=Path(__file__).with_name('BadgeHeroCard.before_glints.swift')
s=base.read_text()
def replace(a,b):
    global s
    assert s.count(a)==1, (a[:100],s.count(a))
    s=s.replace(a,b)

replace('    private let reflectionStage: Badge3DStage\n', '    private let reflectionStage: Badge3DStage\n    private let usesGemShader: Bool\n    private static let gemGlintStrength: Float = STRENGTH\n')
replace('        await applyGemMaterial(to: coin, isMirrorImage: false)', '        let usesGemShader = await applyGemMaterial(to: coin, isMirrorImage: false)')
replace('        await applyGemMaterial(to: mirroredCoin, isMirrorImage: true)', '        _ = await applyGemMaterial(to: mirroredCoin, isMirrorImage: true)')
replace('            reflectionStage: reflectionStage\n', '            reflectionStage: reflectionStage,\n            usesGemShader: usesGemShader\n')
replace('        reflectionStage: Badge3DStage\n', '        reflectionStage: Badge3DStage,\n        usesGemShader: Bool\n')
replace('        self.reflectionStage = reflectionStage\n', '        self.reflectionStage = reflectionStage\n        self.usesGemShader = usesGemShader\n')
replace('    private static func applyGemMaterial(to coin: Entity, isMirrorImage: Bool) async {','    private static func applyGemMaterial(to coin: Entity, isMirrorImage: Bool) async -> Bool {')
replace('        else { return }\n        for (index, material) in model.materials.enumerated()', '        else { return false }\n        for (index, material) in model.materials.enumerated()')
replace('        gemEntity.components.set(model)\n', '        gemEntity.components.set(model)\n        return true\n')
replace('            reflection: reflectionStage.renderer,\n            growth: growth,', '            reflection: reflectionStage.renderer,\n            growth: growth,\n            gemGlintStrength: usesGemShader ? Self.gemGlintStrength : 0,')
replace('    private let finishPipeline: MTLComputePipelineState\n','    private let finishPipeline: MTLComputePipelineState\n    private let gemFlashesPipeline: MTLComputePipelineState\n    private let gemStreaksPipeline: MTLComputePipelineState\n    private let gemPeaksPipeline: MTLComputePipelineState\n    private var gemGlintTargets: GemGlintTargets?\n\n    private struct GemGlintTargets {\n        let flashes: MTLTexture\n        let peaks: MTLTexture\n        let streaks: MTLTexture\n    }\n')
replace('        finishPipeline = try Self.makePipeline(named: "finish", in: library, device: device)', '        finishPipeline = try Self.makePipeline(named: "finish", in: library, device: device)\n        gemFlashesPipeline = try Self.makePipeline(named: "compactGemFlashes", in: library, device: device)\n        gemStreaksPipeline = try Self.makePipeline(named: "gemStreaks", in: library, device: device)\n        gemPeaksPipeline = try Self.makePipeline(named: "gemFlashPeaks", in: library, device: device)')
replace('        reflection reflectionRenderer: RealityRenderer,\n        growth: Float,', '        reflection reflectionRenderer: RealityRenderer,\n        growth: Float,\n        gemGlintStrength: Float = 0,')
replace('        encodeGlowLevels(targets: targets, encoder: encoder)\n        encodeFinish(\n            targets: targets, growth: growth, drawsCoin: true, output: drawable.texture, encoder: encoder\n        )','''        encodeGlowLevels(targets: targets, encoder: encoder)
        let streaks = gemGlintStrength > 0
            ? try encodeGemGlints(targets: targets, encoder: encoder) : nil
        encodeFinish(
            targets: targets, growth: growth, drawsCoin: true, output: drawable.texture,
            encoder: encoder, gemStreaks: streaks, gemGlintStrength: gemGlintStrength
        )''')
replace('        encoder: MTLComputeCommandEncoder\n    ) {\n        var weights = Self.glowWeights', '        encoder: MTLComputeCommandEncoder, gemStreaks: MTLTexture? = nil, gemGlintStrength: Float = 0\n    ) {\n        var strength = gemGlintStrength\n        var weights = Self.glowWeights')
replace('        encoder.setTexture(stagePlate, index: 10)\n', '        encoder.setTexture(stagePlate, index: 10)\n        encoder.setTexture(gemStreaks ?? targets.coin, index: 11)\n        encoder.setBytes(&strength, length: MemoryLayout<Float>.size, index: 4)\n')
replace('    private func encodeGlowLevels(targets: Targets, encoder: MTLComputeCommandEncoder) {','''    /// Only a successfully shaded gem requests these three half-resolution passes.
    /// They use its actual HDR flashes; the other tiers allocate and draw nothing.
    private func encodeGemGlints(targets: Targets, encoder: MTLComputeCommandEncoder) throws -> MTLTexture {
        let width = (targets.coin.width + 1) / 2
        let height = (targets.coin.height + 1) / 2
        if gemGlintTargets?.flashes.width != width || gemGlintTargets?.flashes.height != height {
            gemGlintTargets = GemGlintTargets(
                flashes: try makeTexture(width: width, height: height, usage: [.shaderRead, .shaderWrite]),
                peaks: try makeTexture(width: width, height: height, usage: [.shaderRead, .shaderWrite]),
                streaks: try makeTexture(width: width, height: height, usage: [.shaderRead, .shaderWrite])
            )
        }
        guard let glints = gemGlintTargets else { throw SetupError(failedItem: "gem glints") }
        encoder.setComputePipelineState(gemFlashesPipeline)
        encoder.setTexture(targets.coin, index: 0)
        encoder.setTexture(glints.flashes, index: 1)
        dispatch(covering: glints.flashes, encoder: encoder)
        encoder.setComputePipelineState(gemPeaksPipeline)
        encoder.setTexture(glints.flashes, index: 0)
        encoder.setTexture(glints.peaks, index: 1)
        dispatch(covering: glints.peaks, encoder: encoder)
        encoder.setComputePipelineState(gemStreaksPipeline)
        encoder.setTexture(glints.peaks, index: 0)
        encoder.setTexture(glints.streaks, index: 1)
        dispatch(covering: glints.streaks, encoder: encoder)
        return glints.streaks
    }

    private func encodeGlowLevels(targets: Targets, encoder: MTLComputeCommandEncoder) {''')
replace('                       texture2d<float, access::sample> stagePlate [[texture(10)]],', '                       texture2d<float, access::sample> stagePlate [[texture(10)]],\n                       texture2d<float, access::sample> gemStreaks [[texture(11)]],')
replace('                       constant ContactShadowUniforms &contactShadowPose [[buffer(3)]],', '                       constant ContactShadowUniforms &contactShadowPose [[buffer(3)]],\n                       constant float &gemGlintStrength [[buffer(4)]],')
replace('                    color += glowWeights[level] * glowLevels[level].sample(linearClamp, uv).rgb;\n                }','''                    color += glowWeights[level] * glowLevels[level].sample(linearClamp, uv).rgb;
                }
                if (gemGlintStrength > 0.0) {
                    color += gemGlintStrength * gemStreaks.sample(linearClamp, uv).rgb;
                }''')
replace('    // Halves an image: each output texel averages a 2 x 2 block, read as one', '''    // Camera diffraction from compact, genuine HDR returns. Opaque support
    // at every surrounding sample erodes the outline; broad facets and isolated
    // single-pixel returns cannot seed stars. No time or random input is used.
    kernel void compactGemFlashes(texture2d<float, access::sample> coin [[texture(0)]],
                                  texture2d<float, access::write> flashes [[texture(1)]],
                                  uint2 gid [[thread_position_in_grid]])
    {
        if (gid.x >= flashes.get_width() || gid.y >= flashes.get_height()) return;
        float2 size = float2(coin.get_width(), coin.get_height());
        float2 uv = (float2(gid) * 2.0 + 1.0) / size;
        float4 core = coin.sample(linearClamp, uv);
        // This alpha already makes support zero; avoid sampling the backdrop.
        if (core.a <= 0.995) {
            flashes.write(float4(0.0, 0.0, 0.0, 1.0), gid);
            return;
        }
        float3 mean = float3(0.0);
        uint supportedBrightSamples = 0;
        float alpha = core.a;
        for (int y = -1; y <= 1; y++) {
            for (int x = -1; x <= 1; x++) {
                float4 v = coin.sample(linearClamp, uv + float2(x,y) / size);
                mean += v.rgb / 9.0;
                alpha = min(alpha, v.a);
            }
        }
        float ring[8];
        const float2 directions[8] = {
            float2(1,0), float2(-1,0), float2(0,1), float2(0,-1),
            float2(0.707,0.707), float2(-0.707,0.707),
            float2(0.707,-0.707), float2(-0.707,-0.707)
        };
        for (uint i = 0; i < 8; i++) {
            float4 v = coin.sample(linearClamp, uv + 7.0 * directions[i] / size);
            alpha = min(alpha, v.a);
            ring[i] = dot(v.rgb, float3(0.2126,0.7152,0.0722));
        }
        float brightness = dot(mean, float3(0.2126,0.7152,0.0722));
        for (uint i = 0; i < 4; i++) {
            float3 v = coin.sample(linearClamp, uv + directions[i] / size).rgb;
            supportedBrightSamples += dot(v, float3(0.2126,0.7152,0.0722)) > 0.35 * brightness ? 1 : 0;
        }
        // A neighboring bright facet alone is not an extended flash. Brightness
        // spanning both directions across the source is; reject that extent.
        float extended = max(max(min(ring[0],ring[1]), min(ring[2],ring[3])),
                             max(min(ring[4],ring[7]), min(ring[5],ring[6])));
        float compact = smoothstep(1.5, 4.0, brightness - extended);
        float bright = smoothstep(4.0, 10.0, brightness);
        float supported = smoothstep(0.995, 1.0, alpha);
        float support = supportedBrightSamples >= 3 ? supported : 0.0;
        flashes.write(float4(mean * compact * bright * support, 1.0), gid);
    }

    // One local HDR peak per compact return avoids a cluster of stars and
    // rejects flat plateaus. There is no global ranking or position decal.
    kernel void gemFlashPeaks(texture2d<float, access::sample> flashes [[texture(0)]],
                             texture2d<float, access::write> peaks [[texture(1)]],
                             uint2 gid [[thread_position_in_grid]])
    {
        if (gid.x >= peaks.get_width() || gid.y >= peaks.get_height()) return;
        float2 size = float2(flashes.get_width(), flashes.get_height());
        float2 uv = (float2(gid) + 0.5) / size;
        float3 color = flashes.sample(linearClamp, uv).rgb;
        // A zero source cannot exceed any nonnegative neighboring peak.
        if (all(color == float3(0.0))) {
            peaks.write(float4(0.0, 0.0, 0.0, 1.0), gid);
            return;
        }
        float brightness = dot(color, float3(0.2126,0.7152,0.0722));
        float neighborPeak = 0.0;
        for (int y = -1; y <= 1; y++) {
            for (int x = -1; x <= 1; x++) {
                if (x == 0 && y == 0) continue;
                float3 neighbor = flashes.sample(linearClamp, uv + float2(x,y) / size).rgb;
                neighborPeak = max(neighborPeak, dot(neighbor, float3(0.2126,0.7152,0.0722)));
            }
        }
        peaks.write(float4(brightness > neighborPeak * 1.01 ? color : float3(0.0), 1.0), gid);
    }

    // Four fixed screen directions, with a narrow taper and no extra central
    // blob: the existing fog glow already supplies the photographic halo.
    kernel void gemStreaks(texture2d<float, access::sample> flashes [[texture(0)]],
                          texture2d<float, access::write> streaks [[texture(1)]],
                          uint2 gid [[thread_position_in_grid]])
    {
        if (gid.x >= streaks.get_width() || gid.y >= streaks.get_height()) return;
        float2 size = float2(flashes.get_width(), flashes.get_height());
        float2 uv = (float2(gid) + 0.5) / size;
        float3 color = float3(0.0);
        for (int offset = 2; offset <= 7; offset++) {
            float taper = pow(1.0 - float(offset) / 8.0, 2.0);
            color += taper * (
                flashes.sample(linearClamp, uv + float2(offset,0) / size).rgb
                + flashes.sample(linearClamp, uv - float2(offset,0) / size).rgb
                + flashes.sample(linearClamp, uv + float2(0,offset) / size).rgb
                + flashes.sample(linearClamp, uv - float2(0,offset) / size).rgb
            );
        }
        streaks.write(float4(color, 1.0), gid);
    }

    // Halves an image: each output texel averages a 2 x 2 block, read as one''')
folder=Path(sys.argv[1]); strength=float(sys.argv[2]);folder.mkdir(parents=True,exist_ok=True)
(folder/'BadgeHeroCard.swift').write_text(s.replace('STRENGTH',str(strength)))
print('created',folder,'strength',strength)

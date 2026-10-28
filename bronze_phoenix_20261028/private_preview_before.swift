import SwiftUI
import Metal
import QuartzCore
// RealityKit comes in as @preconcurrency because it has not marked its mesh
// data as Sendable yet; `Badge3DScene` only hands a private copy of it to a
// background task (the mesh edits) and takes the result back.
@preconcurrency import RealityKit
import UIKit

// This file holds the hero badge's slot, the view that loads and poses the
// coin, the RealityKit scene and stage, and the Metal view that shows the
// finished frames. The pass that finishes each frame (`Badge3DImagePipeline`),
// the mesh edits (`Badge3DMeshEdits`) and the data set reads (`Badge3DFiles`)
// are in `Badge3DImagePipeline.swift`.

// MARK: - Live 3D badge

// Everything below draws the hero's badge on its lit stage: a backdrop with the
// light from above and a glossy floor. A tier with a 3D model (see
// `Badge3DModels`) stands on it as a live RealityKit coin; every other tier,
// and the achievement badges, stand on it as their flat art.
//
// The model comes from Blender already prepared for this scene: its bevel
// strips shade like the facets they belong to and its polished metal carries
// no normal maps (both for the nearby point lights used here), and the slice
// that sinks into the floor is already cut away (a floating badge has nothing
// below the floor to cut; see `Badge3DScene.floorY`). So the only changes made to it at load are
// the brushed ring's anisotropy, which USD cannot carry, and the Diamond's gem material, which
// swaps the model's plain `DiamondGem` material for the gem shader (see `Badge3DGem`).

/// Which tiers have a 3D badge, and the data set in Assets.xcassets that holds
/// each one's model: the one place that says so. Adding a tier's 3D badge is
/// one data set (a `Badge3DModel<Tier>` folder holding the tier's `.usdz`) and
/// one changed line here. The switch lists every tier and has no `default`, so
/// a tier added to the ladder cannot be forgotten: the compiler asks for its
/// line.

enum PrivateBadgePreview {
    nonisolated(unsafe) static var selection = UserDefaults.standard.string(forKey: "CoinBadgePreview") ?? "emeraldTrophy"
    static let items: [String: String] = ["waterDrop":"Water Drop","tealSands":"Teal Sands","goldenSands":"Golden Sands","sunrisePath":"Sunrise Path","emeraldSprout":"Emerald Sprout","starAscent":"Star Ascent","islandSunset":"Island Sunset","lightningCompass":"Lightning Compass","zenBalance":"Zen Balance","torchSunburst":"Torch Sunburst","crimsonShield":"Crimson Shield","emeraldArcher":"Emerald Archer","emeraldTrophy":"Emerald Trophy","crescentOcean":"Crescent Ocean","mountainCrest":"Mountain Crest","wingedSword":"Winged Sword"]
    static var datasetName: String? {
        guard items[selection] != nil else { return nil }
        return "Badge3DPreview" + selection.prefix(1).uppercased() + selection.dropFirst()
    }
}

enum Badge3DModels {
    static func datasetName(for tier: MonthlyTier) -> String? {
        if tier == .silver, let dataset = PrivateBadgePreview.datasetName { return dataset }
        switch tier {
        case .iron: return "Badge3DModelIron"
        case .silver: return "Badge3DModelSilver"
        case .copper: return "Badge3DModelCopper"
        case .bronze: return "Badge3DModelBronze"
        case .steel: return "Badge3DModelSteel"
        case .gold: return "Badge3DModelGold"
        case .platinum: return "Badge3DModelPlatinum"
        case .diamond: return "Badge3DModelDiamond"
        }
    }

    /// Achievements and Clean never have a 3D model.
    static func datasetName(for badge: BadgeRef) -> String? {
        switch badge {
        case .tier(let tier): return datasetName(for: tier)
        case .achievement, .clean: return nil
        }
    }

    /// How each tier's badge is shown on the stage: the one place that says
    /// so. Like `datasetName(for:)`, the switch has no `default`, so a tier
    /// added to the ladder asks for its line.
    static func look(for tier: MonthlyTier) -> Badge3DTierLook {
        switch tier {
        case .iron: return Badge3DTierLook(size: 1.03, lift: 0)
        case .copper: return Badge3DTierLook(size: 1.17, lift: 0)
        case .bronze: return Badge3DTierLook(size: 1.10, lift: 0)
        case .steel: return Badge3DTierLook(size: 1.00, lift: 0)
        case .silver: return Badge3DTierLook(size: 0.96, lift: 0)
        case .gold: return Badge3DTierLook(size: 1.00, lift: 0.28)
        case .platinum: return Badge3DTierLook(size: 0.97, lift: 0)
        case .diamond: return Badge3DTierLook(size: 0.98, lift: 0)
        }
    }

    /// The look of any badge: its tier's, or the neutral one for an
    /// achievement or Clean (flat art that is drawn as it is).
    static func look(for badge: BadgeRef) -> Badge3DTierLook {
        switch badge {
        case .tier(let tier): return look(for: tier)
        case .achievement, .clean: return .neutral
        }
    }

    /// The look of the model in `datasetName`. A scene is built per data set,
    /// and a data set belongs to one tier, so the scene finds its tier's look
    /// from the name instead of every caller passing the tier along.
    static func look(forDatasetName datasetName: String) -> Badge3DTierLook {
        if datasetName == "Badge3DPreviewCrimsonShield" { return .neutral }
        if ["Badge3DPreviewCrescentOcean", "Badge3DPreviewMountainCrest", "Badge3DPreviewWingedSword"].contains(datasetName) { return .neutral }
        if datasetName.hasPrefix("Badge3DPreview") { return Badge3DTierLook(size: 0.96, lift: 0.56) }
        let tier = MonthlyTier.allCases.first { self.datasetName(for: $0) == datasetName }
        return tier.map { look(for: $0) } ?? .neutral
    }
}

/// How one badge is shown on the stage.
struct Badge3DTierLook {
    /// How much bigger or smaller the badge is drawn than its model, growing
    /// from its lowest point so its gap to the floor stays what the model has.
    let size: Float
    /// How much higher it floats, in scene units.
    let lift: Float

    /// The model as it is, for a badge with no entry in the table.
    static let neutral = Badge3DTierLook(size: 1, lift: 0)
}

/// The hero's badge slot: the badge on the lit stage, either the live 3D coin
/// or the flat art when the tier has no 3D model.
///
/// Whichever it shows, the slot tells the launch splash when Home's badge is on
/// screen (see `\.markHomeBadgeReady`), so the splash never lifts on a Home
/// without one.
struct Badge3DSlot: View {
    let badge: BadgeRef
    /// The tier to build ahead of time once this slot is set; nil means nothing
    /// to warm (see `Badge3DPreload.slotIsSet`).
    let nextTierToWarm: MonthlyTier?

    var body: some View {
        Badge3DView(badge: badge, nextTierToWarm: nextTierToWarm)
    }
}

/// The flat badge on its own, with no stage, for a slot that cannot draw the
/// stage (a stage that failed to load). It reports to the launch splash the
/// moment it appears: from then on Home's badge spot is not empty.
private struct BadgeFlatWithoutStage: View {
    let badge: BadgeView

    @Environment(\.markHomeBadgeReady) private var markHomeBadgeReady

    var body: some View {
        let markHomeBadgeReadyNow = markHomeBadgeReady
        badge
            // The coin's slot is hidden from VoiceOver and the title beneath
            // names the tier, so the flat badge must not read it twice.
            .accessibilityHidden(true)
            .onAppear { markHomeBadgeReadyNow() }
    }
}

/// The flat badge standing on the lit stage where the 3D coin stands, with its
/// reflection in the floor under it. It is placed in the slot's own
/// coordinates and never signals the launch splash itself: the slot decides
/// what counts as ready (see `Badge3DView`).
private struct BadgeFlatOnStage: View {
    let badge: BadgeRef

    var body: some View {
        let look = Badge3DModels.look(for: badge)
        ZStack(alignment: .top) {
            // Under the badge, so the reflection's blur never dims the badge's
            // own bottom edge, where the two meet at the floor line.
            reflection
            // Sized and lifted like the 3D badge that replaces it, so the swap
            // does not jump. The size grows the badge from its bottom, as the
            // 3D one grows from its lowest point.
            BadgeView(ref: badge, size: Badge3DLayout.flatBadgeSize)
                .scaleEffect(CGFloat(look.size), anchor: .bottom)
                .offset(y: -CGFloat(look.lift) * Badge3DLayout.pointsPerSceneUnit)
        }
        .frame(
            width: Badge3DLayout.flatBadgeSize, height: Badge3DLayout.flatBadgeSize,
            alignment: .top
        )
    }

    /// The badge turned upside down across the floor line: faint, soft, and
    /// fading out with distance from the floor, like the 3D coin's reflection.
    private var reflection: some View {
        BadgeView(ref: badge, size: Badge3DLayout.flatBadgeSize)
            .scaleEffect(x: 1, y: -1)
            .opacity(Badge3DLayout.flatReflectionOpacity)
            .blur(radius: Badge3DLayout.flatReflectionBlurRadius)
            .mask {
                LinearGradient(
                    stops: [
                        .init(color: .black, location: 0),
                        .init(color: .clear, location: Badge3DLayout.flatReflectionFadeFraction),
                    ],
                    startPoint: .top,
                    endPoint: .bottom
                )
            }
            .offset(y: Badge3DLayout.coinHeight)
    }
}

/// Where the coin sits on Home and how scrolling poses it. Every source number
/// is in pixels of the 1080x1440 master frame the Blender scene was framed
/// for, so the live coin lands exactly where the earlier video test drew it.
enum Badge3DLayout {
    /// The slice of the master frame the hero shows: full width, from a
    /// 20-row margin above the coin (row 343) down past the end of its
    /// reflection (row 1200). Nothing above the margin is shown, so the slot
    /// holds no empty rows over the coin.
    static let visibleRect = CGRect(x: 0, y: 343, width: 1080, height: 857)
    /// The part of the master frame RealityKit renders: the visible slice
    /// grown upward until it is centered on the frame's middle row (720). The
    /// camera looks through that middle row and RealityKit has no lens shift,
    /// so an off-center slice cannot be rendered on its own. The extra rows on
    /// top (240 to 343) show above the slot, over the stage.
    static let renderedRect = CGRect(x: 0, y: 240, width: 1080, height: 960)
    /// The slice draws at 47/180 (about 0.261) pt per master pixel on Home,
    /// which puts the coin about 153pt tall. On a 3x screen the render is then
    /// 0.783 pixels per master pixel, which makes the rendered rect a whole
    /// number of pixels both ways (846 by 752); most nearby scales leave a
    /// fraction, which the compositor would resample into a soft image.
    static let pointsPerPixel: CGFloat = 47.0 / 180
    /// The full-size coin's top and bottom edges, in master rows.
    static let coinTopRow: CGFloat = 363
    static let coinBottomRow: CGFloat = 949
    /// How many points one scene unit measures at the coin's distance from the
    /// camera: the lens's 2250 master pixels over the camera's 23 units,
    /// about 97.8 master pixels (see `Badge3DStage`), at `pointsPerPixel`. A
    /// badge's lift is in scene units; the flat badge needs it in points.
    static let pointsPerSceneUnit: CGFloat = 2250 / 23 * pointsPerPixel

    static let sliceSize = CGSize(
        width: visibleRect.width * pointsPerPixel,
        height: visibleRect.height * pointsPerPixel
    )

    /// The side of the flat badge drawn with no stage (see
    /// `BadgeFlatWithoutStage`), the size the hero drew its badge at before
    /// the coin replaced it.
    static let fallbackBadgeSize: CGFloat = 96

    /// The side of the flat badge's frame on the stage. Every tier's art is
    /// drawn in the same square frame, but the shapes differ (chevrons, a
    /// wreath, a hexagon); only Copper is a round disc, 108 of its frame's 120
    /// units across (see `BadgeView.swift`). The stills of every tier are
    /// cropped from renders at this same fixed frame, so whatever their shape
    /// they line up with the 3D badge. One footprint serves every tier: the
    /// frame in which Copper's disc is exactly as wide as the 3D coin.
    static let flatBadgeSize = coinHeight * 120 / 108
    /// How far the flat badge frame's top edge sits below the slice's top
    /// edge. The frame is centered on the coin, so Copper's disc bottom lands
    /// on the coin's bottom row, where the 3D coin meets the floor.
    static let flatBadgeTopInSlice = coinTopInSlice - (flatBadgeSize - coinHeight) / 2
    /// The flat badge's reflection: how faint, how soft (in points of blur),
    /// and over what share of its height it fades out. Tuned by eye against the
    /// 3D coin's reflection, which is also faint and soft and fades with
    /// distance.
    static let flatReflectionOpacity = 0.35
    static let flatReflectionBlurRadius: CGFloat = 2
    static let flatReflectionFadeFraction: CGFloat = 0.4

    /// Where the stage plate (the `Badge3DStagePlate` data set) lies in
    /// master pixels: its top-left corner at (-270, -540), 0.8 plate pixels
    /// per master pixel, as its STAGE_RULES.md sets it. It reaches past both
    /// sides of any iPhone screen, well above the screen's top, and down to
    /// row 1320, behind the top of the title; it fades to black on every
    /// edge, and is already black where the title starts (about row 1260).
    static let stagePlateRect = CGRect(x: -270, y: -540, width: 1620, height: 1860)
    /// The area the finished image covers: the plate's, with its left and
    /// right edges moved out 0.6 master pixels (where the plate is black) so
    /// that every edge sits a whole number of 3x screen pixels from the
    /// rendered rect: 212 on the left and right, 611 above, 94 below. The
    /// coin's render then lands on whole screen pixels inside it.
    static let stageRect = CGRect(
        x: renderedRect.minX - 212 * masterPixelsPerScreenPixel,
        y: renderedRect.minY - 611 * masterPixelsPerScreenPixel,
        width: renderedRect.width + (212 + 212) * masterPixelsPerScreenPixel,
        height: renderedRect.height + (611 + 94) * masterPixelsPerScreenPixel
    )
    /// Master pixels per screen pixel on a 3x screen.
    private static let masterPixelsPerScreenPixel = 1 / (3 * pointsPerPixel)

    static let stageSize = CGSize(
        width: stageRect.width * pointsPerPixel,
        height: stageRect.height * pointsPerPixel
    )
    /// How far the stage's top edge sits from the slice's top edge, in points;
    /// negative, because the stage reaches far above it.
    static let stageTopInSlice = (stageRect.minY - visibleRect.minY) * pointsPerPixel
    /// How far below the slice's top edge the full-size coin's top sits, in
    /// points.
    static let coinTopInSlice = (coinTopRow - visibleRect.minY) * pointsPerPixel
    /// The full-size coin's height in points. It is also the scroll distance
    /// the whole spin is scrubbed across, so the coin winds all the way back
    /// exactly as it leaves the screen.
    static let coinHeight = (coinBottomRow - coinTopRow) * pointsPerPixel

    /// Where the resting coin's top edge sits below the top safe-area edge:
    /// 56pt, 1.4x the quarter inch (40pt) it first got, about 0.35 inch on the
    /// iPhone 13 mini (about 158.7pt per inch), so the coin does not look close
    /// to touching the top of the phone. It also has to stay clear of the edge,
    /// because a coin whose top is above it counts as scrolled and would rest
    /// turned and shrunk (see `growth`).
    static let restingCoinTopBelowSafeArea: CGFloat = 56
    /// How far below the top safe-area edge Home's scroll content starts: the
    /// navigation bar area, where the Settings button sits. Measured on iOS 26
    /// (the scroll inset there is a 62pt safe area plus these 54pt) and tuned
    /// for it alone. The coin's resting top sits inside this area, so the slot
    /// is pulled up by the difference.
    static let navigationAreaHeight: CGFloat = 54
    /// The gap between the slot and the tier title, tuned so the title's
    /// capitals start about 38pt under the point where the reflection fades
    /// out.
    static let titleTopPadding: CGFloat = 16
    /// The slot's top padding, negative on purpose: it lifts the slot, and with
    /// it everything below, out of Home's own top padding and up under the
    /// navigation area until the resting coin's top is
    /// `restingCoinTopBelowSafeArea` below the safe-area edge.
    static let slotTopPadding: CGFloat = restingCoinTopBelowSafeArea
        - navigationAreaHeight - DS.Spacing.homeTopPadding - coinTopInSlice

    /// How grown the coin is for where it sits on screen, from 1 (full size,
    /// face on) down to 0. While the coin's top is below the top safe-area
    /// edge it stays at 1. From the moment its top reaches that edge, each
    /// point scrolled winds the spin back, reaching 0 exactly as the coin's
    /// bottom edge gets there. A pure function of position, so the same scroll
    /// offset always shows the same pose, in either direction.
    static func growth(coinTopInWindow: CGFloat, safeAreaTop: CGFloat) -> Float {
        let distancePastSafeAreaTop = safeAreaTop - coinTopInWindow
        let shrinkProgress = min(1, max(0, distancePastSafeAreaTop / coinHeight))
        return Float(1 - shrinkProgress)
    }
}

/// What a finished frame drew.
private enum Badge3DFrameKind {
    /// The stage alone: backdrop, light and floor, for the flat badge to stand
    /// on.
    case stageOnly
    /// The stage with the live coin and its reflection.
    case withCoin
}

/// The badge on its lit stage. Once the shared studio has loaded, a Metal view
/// draws the stage; a tier with a 3D model then loads its coin, which replaces
/// the flat badge on the stage at its first finished frame, and from then on is
/// posed by where it sits on screen. Every other tier, and the achievement
/// badges, keep their flat badge on the stage.
///
/// A coin that has not drawn six seconds after loading started leaves its flat
/// badge on the stage and the splash stops waiting, but the coin keeps loading:
/// its first frame replaces the flat badge in the same spot. A coin whose
/// model fails to load keeps its flat badge on the stage for the rest of the
/// launch; the other tier's coin is not affected. If the stage itself cannot be
/// built, the flat badge stands alone.
///
/// What tells the launch splash that Home's badge is ready is the first frame
/// of what the slot is going to show: the coin's in a tier with a model, the
/// stage's in one without. A fallback tells it too, as soon as it is decided.
/// The load starts inside the splash's still hold rather than after the splash.
///
/// What the slot shows and tells the splash, by state:
/// - Studio not loaded yet: nothing, until the slot gives up waiting for it
///   (`hasGivenUpWaitingForStudio`). Then the flat badge alone, which tells the
///   splash itself, until the studio arrives.
/// - Studio loaded, no model or the coin not drawn yet: the flat badge on the
///   stage. A tier with no model tells the splash on the stage's first frame;
///   a tier with a model never does here (the stage frames under its loading
///   flat badge say nothing).
/// - Coin drawn (`hasDrawnCoinFrame`): the coin alone, which told the splash
///   on its first frame. After the six second clock it tells the splash a
///   second time, which is harmless.
/// - Clock ran out before the coin drew: the flat badge on the stage, and the
///   splash was told when the clock ran out. The coin keeps loading.
/// - Coin given up on (`hasGivenUpOnCoin`, set only by a failed load): the flat
///   badge on the stage for the rest of the launch; the splash was told when
///   the load failed.
private struct Badge3DView: View {
    let badge: BadgeRef
    /// The tier the preload builds ahead of time once this slot is set. The
    /// caller always decides it; nil means nothing to warm.
    let nextTierToWarm: MonthlyTier?

    /// The data set holding this badge's 3D model; nil when its tier has none.
    private let modelDatasetName: String?

    @Environment(\.homeBadgeMayLoad) private var homeBadgeMayLoad
    @Environment(\.markHomeBadgeReady) private var markHomeBadgeReady
    /// The shared studio, once loaded. A slot built after an earlier one loaded
    /// it starts with it, so a tier promotion never swaps in an empty slot.
    @State private var studio: Badge3DStudio?
    /// Whether this slot gave up waiting for the studio: its load failed, or it
    /// was still loading when the clock ran out. A slot built after an earlier
    /// one gave up starts out that way. While the studio is missing, the flat
    /// badge stands alone; once it arrives the stage takes over and this flag no
    /// longer matters.
    @State private var hasGivenUpWaitingForStudio: Bool
    /// This badge's coin, once its model has loaded (again, a slot built after
    /// that starts with it).
    @State private var scene: Badge3DScene?
    /// The visible slice's top edge in window points. Scrolling Home moves it,
    /// which is what drives the pose. Nil until the first layout pass.
    @State private var sliceTopInWindow: CGFloat?
    /// Whether the live coin has finished a frame. Until then the flat badge
    /// stands on the stage in its place.
    @State private var hasDrawnCoinFrame = false
    /// Whether the stage has finished a frame. The stuck-load clock reads it
    /// for a tier with no model.
    @State private var hasDrawnStageFrame = false
    /// Whether this tier's coin was given up on: its model failed to load. A
    /// coin that is only slow is not given up on (it keeps loading and replaces
    /// the flat badge at its first frame). A slot built after an earlier one
    /// gave up starts out that way, so a tier promotion that rebuilds the slot
    /// cannot bring back a coin that already failed.
    @State private var hasGivenUpOnCoin: Bool
    /// Whether the load holds back until the tier swap has settled. It is set
    /// for any slot built after the launch's first load, not only a tier
    /// promotion (see `waitOutTierSwapIfNeeded`, which also needs a model still
    /// to load).
    @State private var waitsForTierSwapToSettle: Bool

    /// How long a slot has, from the moment loading starts, to draw the first
    /// frame that makes it ready (the coin's in a tier with a model, the
    /// stage's in one without) before the flat badge is kept and the splash
    /// stops waiting. Loading starts inside the splash's still hold, so the
    /// fallback is decided (and the splash can leave) before
    /// `LaunchSplashTimeline.hardCap`, which stays the last resort for a slot
    /// that never reports at all.
    private static let firstFrameDeadlineSeconds: Double = 30

    init(badge: BadgeRef, nextTierToWarm: MonthlyTier?) {
        self.badge = badge
        self.nextTierToWarm = nextTierToWarm
        let modelDatasetName = Badge3DModels.datasetName(for: badge)
        self.modelDatasetName = modelDatasetName
        _studio = State(initialValue: Badge3DStudio.loaded)
        _hasGivenUpWaitingForStudio = State(initialValue: Badge3DStudio.hasBeenGivenUpOn)
        _scene = State(initialValue: modelDatasetName.flatMap { Badge3DScene.loaded(datasetName: $0) })
        _hasGivenUpOnCoin = State(
            initialValue: modelDatasetName.map { Badge3DScene.hasGivenUp(on: $0) } ?? false
        )
        _waitsForTierSwapToSettle = State(initialValue: Badge3DStudio.hasStartedLoading)
    }

    var body: some View {
        // Read here, not inside the `.task` closures or the first-frame
        // closure: an environment read from a captured view copy can come back
        // as the key's default (the same rule `MainTabView.body` follows).
        let mayLoad = homeBadgeMayLoad
        let markReady = markHomeBadgeReady
        // The slice holds the badge's place in the card's layout. The stage is
        // far bigger and spills past it on every side without moving anything
        // (see `Badge3DLayout.stageRect`); it scrolls with the card, and the
        // title, drawn after it, sits on top of its black lower edge.
        Color.clear
            .frame(
                width: Badge3DLayout.sliceSize.width,
                height: Badge3DLayout.sliceSize.height
            )
            .overlay(alignment: .top) {
                stageLayer(markReady: markReady)
            }
            .overlay(alignment: .top) {
                flatBadgeOnStageLayer
            }
            .overlay {
                flatBadgeWithoutStageLayer
            }
            .onGeometryChange(
                for: CGFloat.self,
                of: { proxy in proxy.frame(in: .global).minY },
                action: { sliceTopInWindow = $0 }
            )
            // RealityKit's first use freezes the main thread while its engine
            // starts (about 0.4s on the simulator). Home mounts under the launch
            // splash, so loading waits for `MainTabView` to say the splash is in
            // its still hold, where a freeze is invisible, instead of stalling
            // the splash's moving animation.
            .task(id: mayLoad) {
                guard mayLoad else { return }
                await waitOutTierSwapIfNeeded()
                // A slot torn down during the wait (a second promotion) must
                // not start a load nobody will show.
                guard !Task.isCancelled else { return }
                await loadStageAndCoin(markReady: markReady)
            }
            // The clock runs ALONGSIDE the load, never after it: a load that
            // hangs would otherwise never reach the line that tells the splash
            // to stop waiting.
            // Both tasks start and are cancelled together, and both wait out
            // the tier swap first, so the clock starts with the load.
            .task(id: mayLoad) {
                guard mayLoad else { return }
                await waitOutTierSwapIfNeeded()
                await fallBackIfNoFrameDrawnInTime(markReady: markReady)
            }
            // This slot is set when the frame that makes it ready has drawn,
            // or when its coin's load failed (see `handleFirstFrame` and
            // `loadStageAndCoin`). A coin that missed the six second clock
            // keeps loading and sets the slot at its first frame. Its own
            // badge is fully loaded by then, so the preload (see
            // `Badge3DPreload`) never competes with it.
            .onChange(of: hasDrawnReadyFrame || hasGivenUpOnCoin) { _, isSet in
                if isSet { Badge3DPreload.slotIsSet(showing: badge, nextTierToWarm: nextTierToWarm) }
            }
            // A slot that lives across a month rollover or a publish warms the
            // new month's next tier. Not `initial: true` and only once the slot
            // is set: an earlier call would start the warm build before this
            // slot's own badge has loaded, which the preload's contract forbids.
            .onChange(of: nextTierToWarm) { _, newNextTierToWarm in
                if hasDrawnReadyFrame || hasGivenUpOnCoin {
                    Badge3DPreload.slotIsSet(showing: badge, nextTierToWarm: newNextTierToWarm)
                }
            }
            .allowsHitTesting(false)
            .accessibilityHidden(true)
    }

    // MARK: Layers

    /// The stage, and the coin on it once there is one to draw. Far bigger than
    /// the slice, so it is placed by its own top edge.
    @ViewBuilder
    private func stageLayer(markReady: @escaping @MainActor () -> Void) -> some View {
        if let studio {
            Badge3DRenderer(
                studio: studio,
                scene: hasGivenUpOnCoin ? nil : scene,
                coinTopInWindow: coinTopInWindow,
                onFirstFrame: { kind in
                    handleFirstFrame(of: kind, markReady: markReady)
                }
            )
            .frame(
                width: Badge3DLayout.stageSize.width,
                height: Badge3DLayout.stageSize.height
            )
            .offset(y: Badge3DLayout.stageTopInSlice)
        }
    }

    /// The flat badge on the stage: the whole show for a tier with no model,
    /// and a stand-in for the coin until its first frame, however late (or for
    /// good, once the coin's load failed), so the slot is never empty.
    @ViewBuilder
    private var flatBadgeOnStageLayer: some View {
        if studio != nil, !hasDrawnCoinFrame {
            BadgeFlatOnStage(badge: badge)
                .offset(y: Badge3DLayout.flatBadgeTopInSlice)
        }
    }

    @ViewBuilder
    private var flatBadgeWithoutStageLayer: some View {
        if studio == nil, hasGivenUpWaitingForStudio {
            BadgeFlatWithoutStage(
                badge: BadgeView(ref: badge, size: Badge3DLayout.fallbackBadgeSize)
            )
        }
    }

    // MARK: Loading and the launch splash

    /// A promotion into a tier with a 3D model rebuilds the slot while the
    /// `tierPromotionSwap` animation is still running, and RealityKit's first
    /// use freezes the main thread. Holding the load back until the swap has
    /// settled keeps that freeze out of the animation, which shows the flat
    /// badge meanwhile. Only a slot with a model still to load waits.
    private func waitOutTierSwapIfNeeded() async {
        guard waitsForTierSwapToSettle, modelDatasetName != nil, scene == nil else { return }
        try? await Task.sleep(nanoseconds: UInt64(Animations.tierPromotionSwapSettleSeconds * 1_000_000_000))
    }

    private func loadStageAndCoin(markReady: @MainActor () -> Void) async {
        guard let loadedStudio = await Badge3DStudio.shared() else {
            // No stage: the flat badge stands alone and tells the splash itself.
            // A cancelled slot leaves that to the one that replaces it.
            if !Task.isCancelled {
                hasGivenUpWaitingForStudio = true
            }
            return
        }
        studio = loadedStudio
        // A tier with no model is done: its stage's first frame tells the
        // splash (see `handleFirstFrame`).
        guard let modelDatasetName else { return }
        guard !hasGivenUpOnCoin else {
            // An earlier slot gave up on this coin: the flat badge is already
            // standing, and the splash must not wait for a coin that will not
            // come.
            markReady()
            return
        }
        #if DEBUG
        // Verification only: holds the coin's load past the 6 second clock, so
        // the simulator can show the flat badge being replaced by the coin.
        if ProcessInfo.processInfo.arguments.contains("-Badge3DSlowCoinLoad") {
            try? await Task.sleep(nanoseconds: 15_000_000_000)
        }
        #endif
        let loadedScene = await Badge3DScene.shared(datasetName: modelDatasetName, studio: loadedStudio)
        scene = loadedScene
        // A failed load is cached as nil, so every slot of this launch would
        // fail the same way and this tier keeps the flat badge for the launch.
        // A cancelled slot leaves that to the one that replaces it.
        if loadedScene == nil, !Task.isCancelled {
            Badge3DScene.giveUp(on: modelDatasetName)
            hasGivenUpOnCoin = true
            markReady()
        }
    }

    private func fallBackIfNoFrameDrawnInTime(markReady: @MainActor () -> Void) async {
        try? await Task.sleep(nanoseconds: UInt64(Self.firstFrameDeadlineSeconds * 1_000_000_000))
        // A cancelled clock (the slot was torn down by a tier promotion, a mode
        // switch or a tab switch) must never fall back: the cancelled sleep
        // returns early, and without this it would blame a coin that was simply
        // taken away.
        guard !Task.isCancelled else { return }
        // A model tier whose coin load failed has already told the splash.
        // Otherwise the clock only tells it to stop waiting: the coin keeps
        // loading and replaces the flat badge at its first frame.
        if !hasDrawnReadyFrame, !hasGivenUpOnCoin {
            keepFlatBadge(markReady: markReady)
        }
    }

    /// The frame that makes the slot ready: the coin's first in a tier with a
    /// model, the stage's first in one without.
    private var hasDrawnReadyFrame: Bool {
        modelDatasetName == nil ? hasDrawnStageFrame : hasDrawnCoinFrame
    }

    /// The clock ran out: the flat badge stays as what the slot shows and the
    /// splash stops waiting. The coin is not given up on: it keeps loading and
    /// its first frame replaces the flat badge in the same spot. If the studio
    /// is still loading (the stuck load the clock exists for), the flat badge
    /// stands alone until it arrives, for this slot and every slot built after
    /// it, so no slot is empty while the splash leaves. Never waits for a stage
    /// frame: it may be stuck behind the very coin frame that is late.
    private func keepFlatBadge(markReady: @MainActor () -> Void) {
        if studio == nil {
            Badge3DStudio.giveUp()
            hasGivenUpWaitingForStudio = true
        }
        markReady()
    }

    private func handleFirstFrame(of kind: Badge3DFrameKind, markReady: @MainActor () -> Void) {
        switch kind {
        case .withCoin:
            // A coin whose load failed has no scene to draw, so no coin frame
            // should arrive for it. If one ever did, it must not count as
            // drawn, or the flat badge would be hidden and the slot left a bare
            // stage. A coin that only missed the clock is not given up on: its
            // first frame is the swap that replaces the flat badge.
            guard !hasGivenUpOnCoin else { return }
            hasDrawnCoinFrame = true
            markReady()
        case .stageOnly:
            hasDrawnStageFrame = true
            // In a tier with a model the stage is only what the flat badge
            // stands on while the coin loads (or after its load failed, which
            // tells the splash itself), so its frames never tell the splash
            // anything.
            if modelDatasetName == nil {
                markReady()
            }
        }
    }

    private var coinTopInWindow: CGFloat? {
        guard let sliceTopInWindow else { return nil }
        return sliceTopInWindow + Badge3DLayout.coinTopInSlice
    }
}

/// The UIKit bridge behind `Badge3DView`.
private struct Badge3DRenderer: UIViewRepresentable {
    let studio: Badge3DStudio
    /// The coin to draw on the stage; nil draws the stage alone.
    let scene: Badge3DScene?
    /// Where the full-size coin's top edge sits, in window points; nil until it
    /// has been measured, which leaves the resting coin showing.
    let coinTopInWindow: CGFloat?
    /// Called once per kind of frame, when the first frame of that kind has
    /// finished drawing.
    let onFirstFrame: @MainActor (Badge3DFrameKind) -> Void

    func makeUIView(context: Context) -> Badge3DRenderUIView {
        Badge3DRenderUIView(studio: studio, onFirstFrame: onFirstFrame)
    }

    func updateUIView(_ uiView: Badge3DRenderUIView, context: Context) {
        uiView.show(scene: scene, coinTopInWindow: coinTopInWindow)
    }
}

/// A view whose backing layer is a Metal layer the stage is drawn into, with
/// the coin on it when it has one. It draws only when what it shows changes (a
/// scroll, a new size, a coin arriving), never on a timer, so a still Home
/// costs no rendering at all. The stage alone never changes with the scroll, so
/// it is drawn once per size.
private final class Badge3DRenderUIView: UIView {
    override static var layerClass: AnyClass { CAMetalLayer.self }

    private let studio: Badge3DStudio
    /// The coin drawn on the stage; nil draws the stage alone.
    private var scene: Badge3DScene?
    /// The pose the scroll position asks for. It starts full grown: the
    /// resting, face-on coin.
    private var requestedGrowth: Float = 1
    /// The pose of the coin frame on screen or being drawn; nil forces a
    /// redraw.
    private var drawnGrowth: Float?
    /// Whether the stage-alone frame is on screen or being drawn at the current
    /// size.
    private var isStageDrawn = false
    /// Frames are drawn one at a time: while one is in flight, scroll updates
    /// only move `requestedGrowth`, and the finished frame then chases the
    /// latest request. Asking the layer for a drawable on every scroll event
    /// would block the main thread once all of its drawables were busy.
    private var frameInFlight: Badge3DFrameKind?
    /// The kinds of frame already reported, so each is reported only once.
    private var reportedFrameKinds: Set<Badge3DFrameKind> = []
    private let onFirstFrame: @MainActor (Badge3DFrameKind) -> Void

    init(studio: Badge3DStudio, onFirstFrame: @escaping @MainActor (Badge3DFrameKind) -> Void) {
        self.studio = studio
        self.onFirstFrame = onFirstFrame
        super.init(frame: .zero)
        backgroundColor = .black
        // The stage spreads over the neighboring content; it must never take
        // a touch meant for it.
        isUserInteractionEnabled = false
        if let metalLayer = layer as? CAMetalLayer {
            metalLayer.device = studio.device
            // The AgX view transform already outputs display-encoded sRGB,
            // so the layer stores the values as they are. The finish pass
            // dithers, so 8 bits show no banding.
            metalLayer.pixelFormat = .bgra8Unorm
            // The final pass writes into the drawable from a compute shader.
            metalLayer.framebufferOnly = false
        }
    }

    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }

    override func layoutSubviews() {
        super.layoutSubviews()
        guard let metalLayer = layer as? CAMetalLayer else { return }
        let scale = traitCollection.displayScale
        metalLayer.contentsScale = scale
        // Rounded, so a size like 423.33pt at 3x gives exactly 1270 pixels.
        metalLayer.drawableSize = CGSize(
            width: (bounds.width * scale).rounded(), height: (bounds.height * scale).rounded()
        )
        drawnGrowth = nil
        isStageDrawn = false
        drawRequestedFrameIfIdle()
    }

    func show(scene newScene: Badge3DScene?, coinTopInWindow: CGFloat?) {
        if newScene !== scene {
            scene = newScene
            // Whatever the view shows now has not been drawn yet.
            drawnGrowth = nil
            isStageDrawn = false
        }
        if let coinTopInWindow {
            requestedGrowth = Badge3DLayout.growth(
                coinTopInWindow: coinTopInWindow,
                safeAreaTop: window?.safeAreaInsets.top ?? 0
            )
        }
        drawRequestedFrameIfIdle()
    }

    /// Whether what the view shows differs from what is on screen.
    private var isFrameNeeded: Bool {
        scene == nil ? !isStageDrawn : requestedGrowth != drawnGrowth
    }

    private func drawRequestedFrameIfIdle() {
        guard frameInFlight == nil,
              isFrameNeeded,
              let metalLayer = layer as? CAMetalLayer,
              metalLayer.drawableSize.width > 0,
              let drawable = metalLayer.nextDrawable()
        else { return }
        let onComplete: @Sendable () -> Void = { [weak self] in
            guard let self else { return }
            DispatchQueue.main.async {
                self.frameDidFinish()
            }
        }
        do {
            if let scene {
                try scene.render(growth: requestedGrowth, to: drawable, onComplete: onComplete)
                drawnGrowth = requestedGrowth
                frameInFlight = .withCoin
            } else {
                try studio.imagePipeline.renderStageOnly(to: drawable, onComplete: onComplete)
                isStageDrawn = true
                frameInFlight = .stageOnly
            }
        } catch {
            // Nothing was drawn; the next pose request tries again.
        }
    }

    private func frameDidFinish() {
        let finishedKind = frameInFlight
        frameInFlight = nil
        if let finishedKind, reportedFrameKinds.insert(finishedKind).inserted {
            onFirstFrame(finishedKind)
        }
        drawRequestedFrameIfIdle()
    }
}

/// What every model's scene shares: the image pipeline that finishes each frame
/// (the stage plate, Blender's view transform, the shaders) and the studio's
/// environment lighting, right way up and upside down for the mirror image.
/// Loaded once per launch by whichever slot needs it first; each model's coin is
/// then loaded on top of it (`Badge3DScene`).
///
/// The studio's lights (`Badge3DStudioLight.all`) are plain descriptions, so
/// they are shared by construction; each stage makes its own light entities from
/// them, because an entity can belong to only one parent.
@MainActor
final class Badge3DStudio {
    let imagePipeline: Badge3DImagePipeline
    let lighting: EnvironmentResource
    let mirroredLighting: EnvironmentResource

    var device: MTLDevice { imagePipeline.device }

    // MARK: Loading

    private static var sharedLoad: Task<Badge3DStudio?, Never>?

    /// The studio once its load has finished, for a slot built after that: it
    /// can start with the stage in place instead of waiting a turn for the
    /// finished load task.
    private(set) static var loaded: Badge3DStudio?

    /// Whether the studio was given up on: its load failed, or some slot of
    /// this launch stopped waiting for it. Every slot built afterwards shows
    /// the flat badge alone at once until the studio arrives, instead of an
    /// empty spot. It stays set after the studio arrives, when the slots no
    /// longer look at it.
    private(set) static var hasBeenGivenUpOn = false

    static func giveUp() {
        hasBeenGivenUpOn = true
    }

    static var hasStartedLoading: Bool { sharedLoad != nil }

    /// The one shared studio, loaded on first use. Nil if an asset is missing
    /// or fails to load, which makes the hero slot show its flat badge without a
    /// stage instead of crashing.
    static func shared() async -> Badge3DStudio? {
        if let sharedLoad { return await sharedLoad.value }
        let load = Task {
            let studio = try? await Badge3DStudio.load()
            loaded = studio
            if studio == nil {
                giveUp()
            }
            return studio
        }
        sharedLoad = load
        return await load.value
    }

    private static func load() async throws -> Badge3DStudio {
        // Reading and decoding the bundled files is plain file work, so it
        // stays off the main thread. RealityKit's own loaders are async.
        let files = try await Task.detached(priority: .userInitiated) {
            try Badge3DFiles.readStudio()
        }.value
        // The image pipeline and the two lightings need nothing from each
        // other, so they are built side by side: each one's background work
        // (the plate decode, RealityKit's environment build) runs while
        // another uses the main thread. Every step still runs on the main
        // actor between its awaits, the results are the same objects, and
        // any one failing still fails the whole studio.
        async let imagePipeline = Badge3DImagePipeline(
            agxCube: files.agxCube, stagePlate: files.stagePlate
        )
        async let lighting = EnvironmentResource(equirectangular: files.environmentMap)
        async let mirroredLighting = EnvironmentResource(
            equirectangular: files.upsideDownEnvironmentMap
        )
        return try await Badge3DStudio(
            imagePipeline: imagePipeline, lighting: lighting, mirroredLighting: mirroredLighting
        )
    }

    private init(
        imagePipeline: Badge3DImagePipeline,
        lighting: EnvironmentResource,
        mirroredLighting: EnvironmentResource
    ) {
        self.imagePipeline = imagePipeline
        self.lighting = lighting
        self.mirroredLighting = mirroredLighting
    }
}

/// One model's 3D scene, built once per launch and shared by every hero slot
/// showing it: the coin and its mirror image under the floor, each on its own
/// stage, finished by the shared studio's image pipeline the way Blender's
/// compositor finished the reference render. It renders one frame per request
/// (`render(growth:to:onComplete:)`), never continuously.
///
/// Scene units follow the Blender handoff: Y up, the coin faces +Z, 6.03
/// units across, standing on a floor at Y = -2.895.
@MainActor
final class Badge3DScene {
    /// The floor's height. The coin sinks 0.12 units into it, as on the
    /// Blender stage, and the model file comes with that slice cut away at
    /// this same height (rule 5 of the export's EXPORT_RULES.md), because
    /// RealityKit cannot hide geometry under a floor. The two must stay equal.
    nonisolated static let floorY: Float = -2.895

    private let studio: Badge3DStudio
    private let coinStage: Badge3DStage
    private let reflectionStage: Badge3DStage
    private let usesGemShader: Bool
    private let confinesHighlightGlow: Bool
    /// How this model's tier is shown on the stage (see `Badge3DModels.look`).
    private let look: Badge3DTierLook
    private static let gemGlintStrength: Float = 0.035

    // MARK: Loading

    /// One load per model, keyed by its data set name, so a model loads once
    /// at a time and only a model that is shown, or queued ahead by
    /// `Badge3DPreload`, is loaded. A Release build also drops the models Home
    /// no longer needs (see `keepOnly(datasetNames:)`); a Debug build keeps
    /// every one for the launch.
    private static var loadsByDataset: [String: Task<Badge3DScene?, Never>] = [:]
    private static var loadedByDataset: [String: Badge3DScene] = [:]

    /// The models whose load failed in this launch. Every slot built afterwards
    /// shows that tier's flat badge at once instead of trying again. Per model:
    /// a failed Iron does not make Silver flat. A coin that only missed the
    /// first frame clock is not in here: it keeps loading.
    private static var datasetsGivenUpOn: Set<String> = []

    static func loaded(datasetName: String) -> Badge3DScene? {
        loadedByDataset[datasetName]
    }

    static func hasGivenUp(on datasetName: String) -> Bool {
        datasetsGivenUpOn.contains(datasetName)
    }

    static func giveUp(on datasetName: String) {
        datasetsGivenUpOn.insert(datasetName)
    }

    /// Forgets every finished scene whose model is not in `datasetNames`, so
    /// its memory (about 12 MB each) is freed once no slot is drawing it. A slot
    /// that is drawing one keeps its own strong reference, so this never pulls
    /// a scene out from under the screen.
    ///
    /// A load still in flight is left alone: its task writes the finished
    /// scene back into `loadedByDataset`, which would undo the removal. A load
    /// that failed has no entry there to remove, and that is harmless.
    static func keepOnly(datasetNames: Set<String>) {
        let finishedDatasetNames = Set(loadedByDataset.keys)
        for datasetName in finishedDatasetNames.subtracting(datasetNames) {
            loadedByDataset[datasetName] = nil
            loadsByDataset[datasetName] = nil
        }
    }

    /// The scene of the model in `datasetName`, loaded on first use. Nil if an
    /// asset is missing or fails to load, which makes the hero slot keep its
    /// flat badge instead of crashing.
    static func shared(datasetName: String, studio: Badge3DStudio) async -> Badge3DScene? {
        if let load = loadsByDataset[datasetName] { return await load.value }
        let load = Task {
            let scene = try? await Badge3DScene.load(datasetName: datasetName, studio: studio)
            loadedByDataset[datasetName] = scene
            return scene
        }
        loadsByDataset[datasetName] = load
        return await load.value
    }

    private static func load(datasetName: String, studio: Badge3DStudio) async throws -> Badge3DScene {
        // Copying the bundled model out is plain file work, so it stays off the
        // main thread.
        let modelURL = try await Task.detached(priority: .userInitiated) {
            try Badge3DFiles.writeModelFile(datasetName: datasetName)
        }.value
        let coin = try await Entity(contentsOf: modelURL)
        // Measured before the clone and the flip, once: both stages pose the
        // coin by where its lowest point sits (see `Badge3DStage.pose`).
        let lowestY = coin.visualBounds(relativeTo: nil).min.y
        try await restoreBrushedSteel(in: coin)
        try await restoreShieldFieldBrushing(in: coin)
        let mirroredCoin = coin.clone(recursive: true)
        try await mirrorTopToBottom(mirroredCoin)
        // After the clone and the flip: each copy builds its facet planes
        // from its own mesh, and the mirror image's light is flipped.
        let usesGemShader = await applyGemMaterial(to: coin, isMirrorImage: false)
        _ = await applyGemMaterial(to: mirroredCoin, isMirrorImage: true)
        let look = Badge3DModels.look(forDatasetName: datasetName)
        let coinStage = try Badge3DStage(
            coin: coin,
            environment: studio.lighting,
            lights: Badge3DStudioLight.all,
            isMirrorImage: false,
            lowestY: lowestY,
            look: look
        )
        // The mirror image stands where the coin's reflection appears, so it
        // is lit the way the reflection is: by the studio flipped through the
        // floor.
        let reflectionStage = try Badge3DStage(
            coin: mirroredCoin,
            environment: studio.mirroredLighting,
            lights: Badge3DStudioLight.all.map { $0.mirroredThroughFloor() },
            isMirrorImage: true,
            lowestY: lowestY,
            look: look
        )
        return Badge3DScene(
            studio: studio,
            coinStage: coinStage,
            reflectionStage: reflectionStage,
            usesGemShader: usesGemShader,
            confinesHighlightGlow: coin.findEntity(named: "Casing___smooth_rounded_outer_edge_mobile_geometry") != nil,
            look: look
        )
    }

    private init(
        studio: Badge3DStudio,
        coinStage: Badge3DStage,
        reflectionStage: Badge3DStage,
        usesGemShader: Bool,
        confinesHighlightGlow: Bool,
        look: Badge3DTierLook
    ) {
        self.studio = studio
        self.coinStage = coinStage
        self.reflectionStage = reflectionStage
        self.usesGemShader = usesGemShader
        self.confinesHighlightGlow = confinesHighlightGlow
        self.look = look
    }

    /// Gives the brushed ring back the stretched highlight of its circular
    /// machining marks, which the export dropped: anisotropy 0.4, running
    /// around the coin.
    private static func restoreBrushedSteel(in coin: Entity) async throws {
        guard let casing = coin.findEntity(named: "Casing___smooth_rounded_outer_edge_mobile_geometry"),
              var model = casing.components[ModelComponent.self],
              let brushedIndex = model.materials.firstIndex(where: {
                  $0.name?.hasPrefix("Silver___circumferential_brushed_steel") == true
              }),
              var brushed = model.materials[brushedIndex] as? PhysicallyBasedMaterial
        else { return }
        brushed.anisotropyLevel = 0.4
        brushed.anisotropyAngle = 0.0
        model.materials[brushedIndex] = brushed
        // The highlight stretches along the mesh's tangents, and the imported
        // ones follow the texture atlas, not the machining direction.
        let contents = model.mesh.contents
        let edited = await Task.detached(priority: .userInitiated) {
            Badge3DMeshEdits.withCircumferentialTangents(contents, onPartsUsing: brushedIndex)
        }.value
        model.mesh = try await MeshResource(from: edited)
        casing.components.set(model)
    }

    /// Flips every mesh under `entity` top to bottom, for the mirror image
    /// under the floor. The flip is baked into the mesh data because RealityKit
    /// lights a model with a negative scale as if its normals pointed inward.
    private static func restoreShieldFieldBrushing(in entity: Entity) async throws {
        if var model = entity.components[ModelComponent.self] {
            var fieldMaterialIndices: Set<Int> = []
            for (index, material) in model.materials.enumerated()
            where material.name == "CrimsonShield_BrushedField" {
                guard var field = material as? PhysicallyBasedMaterial else { continue }
                field.anisotropyLevel = 0.55
                field.anisotropyAngle = 0.0
                model.materials[index] = field
                fieldMaterialIndices.insert(index)
            }
            if !fieldMaterialIndices.isEmpty {
                let contents = model.mesh.contents
                let edited = await Task.detached(priority: .userInitiated) {
                    Badge3DMeshEdits.withShieldFieldTangents(
                        contents, onPartsUsing: fieldMaterialIndices
                    )
                }.value
                model.mesh = try await MeshResource(from: edited)
                entity.components.set(model)
            }
        }
        for child in entity.children {
            try await restoreShieldFieldBrushing(in: child)
        }
    }

    private static func mirrorTopToBottom(_ entity: Entity) async throws {
        if var model = entity.components[ModelComponent.self] {
            let contents = model.mesh.contents
            let mirrored = await Task.detached(priority: .userInitiated) {
                Badge3DMeshEdits.mirroredTopToBottom(contents)
            }.value
            model.mesh = try await MeshResource(from: mirrored)
            entity.components.set(model)
        }
        for child in entity.children {
            try await mirrorTopToBottom(child)
        }
    }

    /// Swaps the material named `Badge3DGem.materialName` for the gem shader,
    /// on the coin or on its mirror image. A model without that material
    /// (every tier but the Diamond) is left exactly as it is; so is a gem
    /// whose shader or planes cannot be built, which then keeps its plain
    /// material and is lit like any other model.
    private static func applyGemMaterial(to coin: Entity, isMirrorImage: Bool) async -> Bool {
        guard let gemEntity = entityWithGemMaterial(in: coin),
              var model = gemEntity.components[ModelComponent.self],
              let gem = await Badge3DGem.shared(),
              let gemMaterial = try? await gem.material(
                  for: model.mesh.contents, isMirrorImage: isMirrorImage
              )
        else { return false }
        for (index, material) in model.materials.enumerated()
        where material.name == Badge3DGem.materialName {
            model.materials[index] = gemMaterial
        }
        gemEntity.components.set(model)
        return true
    }

    private static func entityWithGemMaterial(in entity: Entity) -> Entity? {
        if let model = entity.components[ModelComponent.self],
           model.materials.contains(where: { $0.name == Badge3DGem.materialName }) {
            return entity
        }
        for child in entity.children {
            if let found = entityWithGemMaterial(in: child) { return found }
        }
        return nil
    }

    // MARK: Rendering

    /// Poses both stages for `growth` and draws one finished frame into
    /// `drawable`, which is presented as soon as the GPU is done.
    /// `onComplete` runs on a background thread after that.
    func render(
        growth: Float,
        to drawable: CAMetalDrawable,
        onComplete: @escaping @Sendable () -> Void
    ) throws {
        coinStage.pose(growth: growth, mirrored: false)
        reflectionStage.pose(growth: growth, mirrored: true)
        try studio.imagePipeline.render(
            coin: coinStage.renderer,
            reflection: reflectionStage.renderer,
            look: look,
            confinesHighlightGlow: confinesHighlightGlow,
            gemGlintStrength: usesGemShader ? Self.gemGlintStrength : 0,
            to: drawable,
            onComplete: onComplete
        )
    }
}

/// Builds 3D badge scenes in the background, ahead of the slot that will show
/// them, so a tier's coin is on screen at once instead of the flat badge for
/// the second a first build takes. It builds through `Badge3DScene.shared`,
/// like a slot does, so a slot that needs a tier whose build is still running
/// waits for that same build instead of starting another.
///
/// What it builds depends on the build configuration:
/// - Every build: the month's next tier, which the caller decides
///   (`nextTierToWarm`), so a real level-up shows the new tier's coin the
///   moment it is promoted, whatever badge Home shows. That costs one more
///   scene in memory (about 11 MB on the simulator) in exchange for no flat
///   badge at the level-up. The caller passes nil when nothing is left to warm
///   (the top tier has nothing above it), and then nothing is queued.
/// - Debug builds only: after that, every tier in ladder order, once per
///   launch, for the Home "Badge preview" row, so stepping the preview through
///   the ladder shows each coin at once. All eight scenes cost about 75 MB.
///   That part exists for the preview row and is deleted together with it.
/// - Release builds only: every scene except the shown badge's and the warm
///   tier's is dropped, so three tiers shown in a row cost two scenes of
///   memory, not three (see `keepOnlyShownAndNextScenes`).
@MainActor
private enum Badge3DPreload {
    /// Only Debug builds read this (see `slotIsSet`).
    private static var hasQueuedEveryTier = false

    /// Starts the background builds for a hero slot that is set: the frame that
    /// makes it ready has drawn, or its coin's load failed. That is also when
    /// the slot tells the launch splash it is ready, so the hero's own badge
    /// always loads first and alone, the splash never waits behind another
    /// tier, and the builds start during the splash's last moments and its
    /// exit. (After the six second clock the splash is told at the clock, while
    /// the slot is set only at the coin's first frame, so the builds wait for
    /// the coin.) After a level-up the new slot calls it too, which warms the
    /// month's next tier again.
    ///
    /// `nextTierToWarm` is the one tier to build and to keep, decided by the
    /// caller: there is no fallback in here, and nil means nothing to warm.
    /// The same value goes to the scenes that are kept, so what is kept and
    /// what is built can never disagree.
    ///
    /// It only reads the studio, never loads it: with no studio yet (still
    /// loading, or given up on) there is nothing to build on, and a later slot
    /// tries again.
    static func slotIsSet(showing badge: BadgeRef, nextTierToWarm: MonthlyTier?) {
        // First, above both guards below: no warm tier (a Diamond, say) returns
        // early from them, and there are still scenes to let go of.
        #if !DEBUG
        keepOnlyShownAndNextScenes(showing: badge, nextTierToWarm: nextTierToWarm)
        #endif
        guard let studio = Badge3DStudio.loaded else { return }

        var tiersToBuild: [MonthlyTier] = []
        if let nextTierToWarm {
            tiersToBuild.append(nextTierToWarm)
        }
        #if DEBUG
        if !hasQueuedEveryTier {
            hasQueuedEveryTier = true
            tiersToBuild += MonthlyTier.allCases
        }
        #endif
        guard !tiersToBuild.isEmpty else { return }

        // Not a slot's `.task`, so tearing a slot down cancels nothing here.
        // One task per call, building its own list, so a build that hangs
        // delays only the tiers behind it in that list.
        Task { @MainActor in
            for tier in tiersToBuild {
                await buildSceneIfNeeded(for: tier, studio: studio)
            }
        }
    }

    /// Frees the scenes of every tier Home is not showing and is not about to
    /// show: it keeps the shown badge's scene and the warm tier's. An
    /// achievement or Clean on Home has no scene of its own, so only the warm
    /// tier's scene (and a build still in flight) survives. Compiled in every
    /// configuration so Debug builds type-check it too, but only Release calls
    /// it: Debug keeps every scene for the "Badge preview" row.
    private static func keepOnlyShownAndNextScenes(
        showing badge: BadgeRef, nextTierToWarm: MonthlyTier?
    ) {
        var datasetNamesToKeep: Set<String> = []
        if let shownDatasetName = Badge3DModels.datasetName(for: badge) {
            datasetNamesToKeep.insert(shownDatasetName)
        }
        if let nextTierToWarm,
            let warmDatasetName = Badge3DModels.datasetName(for: nextTierToWarm)
        {
            datasetNamesToKeep.insert(warmDatasetName)
        }
        Badge3DScene.keepOnly(datasetNames: datasetNamesToKeep)
    }

    /// One tier at a time keeps the main thread's share small. A tier already
    /// built, or given up on by a slot, is skipped.
    private static func buildSceneIfNeeded(for tier: MonthlyTier, studio: Badge3DStudio) async {
        guard let datasetName = Badge3DModels.datasetName(for: tier),
              Badge3DScene.loaded(datasetName: datasetName) == nil,
              !Badge3DScene.hasGivenUp(on: datasetName)
        else { return }
        _ = await Badge3DScene.shared(datasetName: datasetName, studio: studio)
    }
}

/// What the Diamond's gem look is made of: the surface shader that traces the
/// studio's light through the stone (`BadgeGemSurface.metal`) and the studio's
/// light it reads. Loaded once per launch, by the first model that has a gem
/// material, and shared by every slot. Each coin copy then builds its own
/// material, because the shader needs that copy's facet planes (the mirror
/// image's mesh is flipped, so its planes are too).
///
/// RealityKit's own materials cannot bend light through a stone, so the gem is
/// a `CustomMaterial`: our Metal code runs for every pixel of the gem. It
/// needs a convex gem (`GemFacetPlanes`), so a model that is not one keeps
/// its plain material.
@MainActor
private final class Badge3DGem {
    /// A model material with this name asks for the gem shader.
    nonisolated static let materialName = "DiamondGem"
    /// The shader function in `BadgeGemSurface.metal`.
    private static let shaderFunctionName = "badgeGemSurface"

    private let surfaceShader: CustomMaterial.SurfaceShader
    /// The studio's full-strength light, as an equirectangular HDR texture
    /// with its mipmaps (the shader reads a sharp and a blurred level).
    private let studioLight: TextureResource

    // MARK: Loading

    private static var sharedLoad: Task<Badge3DGem?, Never>?

    /// The one shared gem, loaded on first use. Nil if the shader or the
    /// light fails to load, which leaves the Diamond on its plain material.
    static func shared() async -> Badge3DGem? {
        if let sharedLoad { return await sharedLoad.value }
        let load = Task { try? await Badge3DGem.load() }
        sharedLoad = load
        return await load.value
    }

    private static func load() async throws -> Badge3DGem {
        guard let library = MTLCreateSystemDefaultDevice()?.makeDefaultLibrary() else {
            throw Badge3DFiles.LoadError(failedItem: "default Metal library")
        }
        let surfaceShader = CustomMaterial.SurfaceShader(named: shaderFunctionName, in: library)
        let lightImage = try await Task.detached(priority: .userInitiated) {
            try Badge3DFiles.readGemEnvironment()
        }.value
        let studioLight = try await TextureResource(
            image: lightImage,
            options: TextureResource.CreateOptions(semantic: .hdrColor, mipmapsMode: .allocateAndGenerateAll)
        )
        return Badge3DGem(surfaceShader: surfaceShader, studioLight: studioLight)
    }

    private init(surfaceShader: CustomMaterial.SurfaceShader, studioLight: TextureResource) {
        self.surfaceShader = surfaceShader
        self.studioLight = studioLight
    }

    // MARK: Material

    /// The gem material for the mesh `contents`: unlit (the shader's result
    /// is the color, because the studio's light is already in it), with the
    /// mesh's facet planes in the base color texture slot (one pixel per
    /// plane) and the studio's light in the custom one. Nil when the mesh is
    /// not a convex gem.
    func material(for contents: MeshResource.Contents, isMirrorImage: Bool) async throws -> CustomMaterial? {
        let planes = await Task.detached(priority: .userInitiated) {
            GemFacetPlanes.outwardPlanes(ofTriangles: Self.triangleCorners(of: contents))
        }.value
        guard let planes else { return nil }
        var material = try CustomMaterial(surfaceShader: surfaceShader, lightingModel: .unlit)
        material.baseColor.texture = CustomMaterial.Texture(try Self.planeTexture(for: planes))
        material.custom.texture = CustomMaterial.Texture(studioLight)
        // The mirror image is lit by the studio flipped through the floor.
        material.custom.value = SIMD4(isMirrorImage ? 1 : 0, 0, 0, 0)
        return material
    }

    /// Every triangle of the mesh as three consecutive corners.
    nonisolated private static func triangleCorners(of contents: MeshResource.Contents) -> [SIMD3<Float>] {
        var corners: [SIMD3<Float>] = []
        for model in contents.models {
            for part in model.parts {
                let positions = part.positions.elements
                if let triangleIndices = part.triangleIndices {
                    corners += triangleIndices.elements.map { positions[Int($0)] }
                } else {
                    corners += positions
                }
            }
        }
        return corners
    }

    /// One pixel per plane: the unit outward normal in red, green and blue and
    /// the offset in alpha. The shader reads it at half precision, which is
    /// why it traces with a small tolerance (see `BadgeGemSurface.metal`).
    private static func planeTexture(for planes: [SIMD4<Float>]) throws -> TextureResource {
        let planeData = planes.withUnsafeBytes { Data($0) }
        return try TextureResource(
            dimensions: .dimensions(width: planes.count, height: 1),
            format: .raw(pixelFormat: .rgba32Float),
            contents: .init(mipmapLevels: [.mip(data: planeData, bytesPerRow: planeData.count)])
        )
    }
}

/// One RealityKit renderer with its own copy of the studio: a coin on a
/// turntable, the lights, the camera. The coin and its mirror image each get
/// one because RealityKit cannot keep a light off an entity, and the mirror
/// image needs the studio flipped through the floor while the coin needs it
/// the right way up.
@MainActor
final class Badge3DStage {
    static let cameraPosition: SIMD3<Float> = [0, 1.8, 23]
    static let cameraTarget: SIMD3<Float> = [0, -0.55, 0]
    /// A 75mm lens on a 36mm-wide sensor that spans the master frame's 1080
    /// pixels.
    static let focalLengthInPixels: Float = 75 / 36 * 1080
    /// The environment map's brightness, in stops. The bundled map already
    /// carries each light's fitted share (see `Badge3DFiles`), so it is
    /// used as it is.
    private static let environmentExposure: Float = 0

    let renderer: RealityRenderer
    private let turntable = Entity()
    /// The model's lowest point at full size, in scene units, and how the
    /// tier's look sizes and lifts it (see `pose`).
    private let lowestY: Float
    private let look: Badge3DTierLook

    init(
        coin: Entity,
        environment: EnvironmentResource,
        lights: [Badge3DStudioLight],
        isMirrorImage: Bool,
        lowestY: Float,
        look: Badge3DTierLook
    ) throws {
        self.lowestY = lowestY
        self.look = look
        renderer = try RealityRenderer()
        renderer.lighting.resource = environment
        renderer.lighting.intensityExponent = Self.environmentExposure
        // Transparent where there is no coin, so the image pipeline can lay
        // the coin over its reflection.
        renderer.cameraSettings.colorBackground = .color(CGColor(gray: 0, alpha: 0))
        // Scene-linear light out: the image pipeline applies Blender's own
        // view transform instead of RealityKit's.
        renderer.cameraSettings.isToneMappingEnabled = false
        // The reflection is dim, faded and meant to look soft, so only the
        // coin pays for 4x multisampling.
        renderer.cameraSettings.antialiasing = isMirrorImage ? .none : .multisample4X

        let stage = Entity()
        // The environment map was baked with its center facing +Z, the coin's
        // front. RealityKit centers an environment on -Z, so the whole stage
        // turns half a circle to face its lights the way it did in Blender.
        stage.orientation = simd_quatf(angle: .pi, axis: [0, 1, 0])
        turntable.addChild(coin)
        stage.addChild(turntable)
        for light in lights {
            stage.addChild(light.makeEntity())
        }
        let camera = Entity()
        camera.components.set(
            PerspectiveCameraComponent(
                near: 1,
                far: 100,
                fieldOfViewInDegrees: Self.horizontalFieldOfViewDegrees,
                // Blender fitted the sensor horizontally; RealityKit's field
                // of view is vertical unless told otherwise.
                fieldOfViewOrientation: .horizontal
            )
        )
        stage.addChild(camera)
        camera.look(at: Self.cameraTarget, from: Self.cameraPosition, relativeTo: stage)
        renderer.entities.append(stage)
        renderer.activeCamera = camera
    }

    private static var horizontalFieldOfViewDegrees: Float {
        let halfWidthInPixels: Float = 540
        return 2 * atan(halfWidthInPixels / focalLengthInPixels) * 180 / .pi
    }

    /// The Blender animation at `growth` (its t, 0 to 1, all linear): one full
    /// turn about +Y, uniform scale t, and the center rising from the floor to
    /// Y = 0. The angle comes from t directly; interpolating between the 0 and
    /// 360 degree orientations would find no spin at all. The mirror image
    /// takes the same pose reflected through the floor: its mesh is already
    /// flipped top to bottom, and a flip commutes with a turn about Y, so only
    /// its center moves, as far below the floor as the coin's is above it.
    ///
    /// The tier's look then sizes and lifts the badge. The size scales it
    /// about its lowest point, so a bigger badge grows upward and keeps its
    /// float gap, and the lift raises that point. Both ride on `growth`, so
    /// the badge still reaches the floor as it shrinks away.
    func pose(growth: Float, mirrored: Bool) {
        // At zero size every transform collapses to a point; hide the coin
        // rather than hand the renderer a degenerate matrix.
        turntable.isEnabled = growth > 0
        guard growth > 0 else { return }
        let centerRiseY = lowestY * (1 - look.size) + look.lift
        let centerY = Badge3DScene.floorY * (1 - growth) + growth * centerRiseY
        turntable.transform = Transform(
            scale: SIMD3(repeating: growth * look.size),
            rotation: simd_quatf(angle: Self.spinAngle(growth: growth), axis: [0, 1, 0]),
            translation: [0, mirrored ? 2 * Badge3DScene.floorY - centerY : centerY, 0]
        )
    }

    /// How far the coin has turned about +Y at `growth`, in radians.
    nonisolated static func spinAngle(growth: Float) -> Float {
        2 * .pi * growth
    }
}

/// A point light standing in for part of one of the Blender studio's area
/// lights (see `all`).
struct Badge3DStudioLight {
    let position: SIMD3<Float>
    /// Linear RGB, as in the Blender scene.
    let color: SIMD3<Float>
    /// RealityKit lumens, calibrated against the Blender light's own render.
    let intensity: Float

    /// The studio's lights, placed where Blender's are. An environment map
    /// holds lights infinitely far away, so every point of a flat emblem facet
    /// sees them from the same direction and the facet turns one flat tone;
    /// these nearby lights are what give the facets Blender's gradients.
    ///
    /// RealityKit has no area lights and draws at most 8 lights, so each
    /// Blender softbox is stood in for by points on its surface, and the
    /// overhead spot, which barely reaches the coin's face, is left out
    /// (adding it measured worse). The intensities were fitted, together
    /// with how much of each light stays in the environment map (see the
    /// `Badge3DEnvironment` data set), to Blender's per-light renders at
    /// poses 0, 20, 45, 90 and 180 degrees, minimizing the difference after
    /// the AgX view transform.
    static let all: [Badge3DStudioLight] = [
        // Key, the tall softbox up and to the left.
        Badge3DStudioLight(position: [-5.4, 3.5, 2.8], color: [1, 0.98, 0.95], intensity: 1_156_500),
        // Rim, the narrow strip to the right: its upper end, middle and lower end.
        Badge3DStudioLight(position: [5.393, 2.023, 3.426], color: [0.98, 0.99, 1], intensity: 226_633),
        Badge3DStudioLight(position: [4.8, 1.8, 4.2], color: [0.98, 0.99, 1], intensity: 226_633),
        Badge3DStudioLight(position: [4.207, 1.577, 4.974], color: [0.98, 0.99, 1], intensity: 226_633),
        // Top, the crown light above.
        Badge3DStudioLight(position: [-0.3, 5.1, 3.5], color: [1, 0.99, 0.98], intensity: 958_800),
        // Bottom, the narrow reflector low on the left: its lower and upper ends.
        Badge3DStudioLight(position: [-2.075, -2.375, 4.375], color: [1, 0.985, 0.96], intensity: 300_000),
        Badge3DStudioLight(position: [-1.525, -1.825, 4.825], color: [1, 0.985, 0.96], intensity: 300_000),
        // Fill, the large card in front.
        Badge3DStudioLight(position: [0, 0.6, 7.5], color: [1, 1, 1], intensity: 83_800),
    ]

    func mirroredThroughFloor() -> Badge3DStudioLight {
        Badge3DStudioLight(
            position: SIMD3(position.x, 2 * Badge3DScene.floorY - position.y, position.z),
            color: color,
            intensity: intensity
        )
    }

    @MainActor
    func makeEntity() -> Entity {
        let entity = Entity()
        entity.position = position
        entity.components.set(
            PointLightComponent(
                cgColor: CGColor(
                    red: CGFloat(color.x), green: CGFloat(color.y), blue: CGFloat(color.z), alpha: 1
                ),
                intensity: intensity,
                // Far beyond the scene, so the light falls off with the
                // inverse square of distance, as a real light does.
                attenuationRadius: 100
            )
        )
        return entity
    }
}

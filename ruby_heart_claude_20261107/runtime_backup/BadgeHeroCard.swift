import SwiftUI

/// The view-facing live tail: the running source's UNBANKED net seconds, split
/// per day through the same `ReclaimedTimeCalculator.liveSecondsByDay` and
/// `BadgeEngine.liveTailByDay` the badge evaluation itself uses, then reduced
/// to one month's share. Every badge surface (hero, Badges screen, tier
/// celebration) adds exactly this onto a base the presenter already de-tailed
/// by the same share, for the live month only. Reading the engine's own
/// functions rather than re-deriving is what makes the never-double-count
/// guarantee auditable, and the per day split is what keeps an overnight
/// block's evening in the month total after midnight.
extension LiveReclaimedSnapshot {
    func badgeLiveTailSeconds(now: Date, inMonth monthKey: String) -> Int {
        // Gregorian, like the coordinator: the stamps must match the month keys.
        let calendar = LocalDay.calendar()
        let secondsByDay = ReclaimedTimeCalculator.liveSecondsByDay(
            sourceStart: activeSourceStart,
            sourceEnd: activeSourceEnd,
            bypasses: activeSourceBypasses,
            now: now,
            calendar: calendar
        )
        return BadgeStatePresenter.tailSeconds(
            BadgeEngine.liveTailByDay(from: secondsByDay, calendar: calendar),
            inMonth: monthKey
        )
    }

    /// Whether a source (a scheduled block or a Quick Start) is running right
    /// now. The badge surfaces read it to pick their tick cadence and to light
    /// the live dot, so they all agree on what "live" means.
    var isSourceLive: Bool { activeSourceStart != nil }
}

/// The Home badge hero, top to bottom, all centered: the badge, which is the
/// one control that opens the All badges layer; a "You earned <badge>" title;
/// one line saying what is left to earn ("Protect 28 more hours to earn
/// Silver"); and a thick progress bar that spans the page's content width.
///
/// The badge and its name are Automatic's (this month's tier while
/// `BadgeConfig.homeBadgeIsMonthlyOnly` is on, the newest earned badge when it
/// is off) unless the user chose another earned badge
/// (`BadgeViewModeling.homeBadgeChoice`). The bar and the line never follow
/// either one: they keep tracking the month, and in monthly mode the line then
/// says "this month" (`MonthlyHeroLine`).
///
/// Live behavior: the monthly number ticks per minute (the app's standard
/// cadence) by adding the CURRENT live month's share of the running tail onto
/// the published banked base: the presenter already subtracted the
/// evaluation's running tail from that base, so nothing is ever counted twice.
/// The displayed tier is `max(floorTier, tier(base + tail))`, so crossing a
/// threshold promotes the badge on the very next tick, independent of the
/// celebration (§4.1).
struct BadgeHeroCard: View {
    /// Opens the badges landing over Home.
    let onSeeAll: () -> Void

    @Environment(\.badges) private var badges
    @Environment(\.liveReclaimed) private var liveReclaimed
    /// Reduce Motion: a tier promotion swaps instantly (crossfade only, no
    /// scale settle, no bar choreography), and the line's digit roll becomes a
    /// crossfade.
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    /// The tier the hero currently SHOWS. On a promotion it trails the
    /// computed tier by the short choreography in
    /// `handleComputedTierChange(to:)` so the user sees the full bar →
    /// badge swap → fresh bar story instead of everything snapping on one
    /// minute tick. `nil` until the first render seeds it.
    @State private var displayedTier: MonthlyTier?
    /// Opacity of the bar AND the line under the title ("Protect 28 more
    /// hours to earn Silver") during the promotion choreography: both fade
    /// out, snap to the new segment while invisible, and fade back in with the
    /// fresh climb. A visible full → near-zero width change would read as
    /// draining, the opposite of what happened.
    @State private var promotionBarOpacity: Double = 1
    /// Re-entry guard: per-minute ticks during the ~0.85s run (0.67s of
    /// beats + the trailing bar fade-in) must not start a second
    /// choreography.
    @State private var promotionInFlight = false
    /// The pick Home shows, which trails the live pick by
    /// `Animations.homeBadgeSwapAfterPick`. A new pick waits because the first
    /// draw of a tier costs 59 to 212 ms of main thread on the simulator (more
    /// on a phone), so the 3D rebuild must start after the picker sheet's
    /// close. Only the last pick inside the wait is applied. nil means no pick
    /// has been applied yet (the first render, which follows the live pick).
    @State private var appliedPick: AppliedPick?
    #if DEBUG
    /// Debug only badge preview: the tier whose badge and name replace the real
    /// ones while the owner flips through the ladder. It never touches progress,
    /// and `nil` means the real badge shows.
    @State private var previewTier: MonthlyTier? = .silver
    @State private var previewCoin = PrivateBadgePreview.selection
    #endif

    /// A pick Home has applied. `badge` is nil when the pick was Automatic. A
    /// wrapper rather than a bare `BadgeRef?` so `appliedPick == nil` can mean
    /// "not set yet" while an applied Automatic is still a value.
    private struct AppliedPick: Equatable {
        let badge: BadgeRef?
    }

    init(onSeeAll: @escaping () -> Void) {
        self.onSeeAll = onSeeAll
    }

    var body: some View {
        if let badges, badges.state.ready, let hero = badges.state.hero {
            // The user's live pick, or nil when there is none or it is no
            // longer earned. Resolved here, beside the state it is checked
            // against, so the view model's stored value never reaches the
            // screen raw.
            let liveChoice = BadgeStatePresenter.validHomeBadgeChoice(
                badges.homeBadgeChoice, in: badges.state
            )
            // Home shows the APPLIED pick, re-checked against what is earned at
            // every render, so a pick that stopped being earned (Delete All
            // Data) disappears at once. Only before the first apply does it
            // follow the live pick.
            let shownPick: BadgeRef? = if let appliedPick {
                BadgeStatePresenter.validHomeBadgeChoice(appliedPick.badge, in: badges.state)
            } else {
                liveChoice
            }
            // The user's pick wins. Without one, Automatic decides: this
            // month's tier while `BadgeConfig.homeBadgeIsMonthlyOnly` is on,
            // the newest earned badge when it is off. It replaces the hero's
            // badge only when it is a different one (nil keeps the month's own
            // tier, promotion and all).
            let chosen = shownPick ?? BadgeStatePresenter.automaticOverride(in: badges.state)
            card(hero: hero, state: badges.state, chosen: chosen)
                .task(id: liveChoice) {
                    await applyLivePick(liveChoice)
                }
        }
    }

    // MARK: Applying the pick

    /// Brings `appliedPick` up to the live pick. The first run applies it at
    /// once, so a launch shows the stored pick with no swap. A later change
    /// waits `Animations.homeBadgeSwapAfterPick` first, even while Home is
    /// covered, so the 3D rebuild lands under the Badges screen once the picker
    /// has closed and Home is already finished when the user comes back. A
    /// second pick inside the wait cancels this task (its id changes), so
    /// browsing rebuilds the slot once, for the last pick only.
    private func applyLivePick(_ liveChoice: BadgeRef?) async {
        guard let currentPick = appliedPick else {
            appliedPick = AppliedPick(badge: liveChoice)
            return
        }
        guard currentPick.badge != liveChoice else { return }
        try? await Task.sleep(for: .seconds(Animations.homeBadgeSwapAfterPick))
        guard !Task.isCancelled else { return }
        appliedPick = AppliedPick(badge: liveChoice)
        #if DEBUG
        // A new pick must show: the Debug preview would otherwise keep standing
        // in for it. Cleared here, as the pick reaches Home, so the 3D slot is
        // rebuilt once, not again during the picker's close.
        previewTier = nil
        #endif
    }

    private func card(hero: BadgeHeroState, state: BadgeUIState, chosen: BadgeRef?) -> some View {
        VStack(spacing: 0) {
            if let progress = hero.monthlyProgress {
                TimelineView(
                    .periodic(
                        from: .now, by: progress.isLive && liveReclaimed.isSourceLive ? 60 : 3600
                    )
                ) { context in
                    monthlyContent(progress: progress, chosen: chosen, now: context.date)
                }
            } else {
                achievementContent(
                    hero: hero, chosen: chosen,
                    // The install month has tiers too, and so does any other
                    // month an achievement is on Home: warm the month's next
                    // tier so its first crossing loads warm.
                    nextTierToWarm: BadgeStatePresenter.currentMonthTier(in: state)
                        .flatMap(BadgeConfig.nextTier(after:))
                )
            }

            // Closes the badge section on the flat page with a section line:
            // the full seam over it, and the seam minus the 14pt Home stack
            // spacing under it.
            DS.SectionLine()
                .padding(.top, DS.Spacing.sectionSeam)
                .padding(.bottom, DS.Spacing.sectionSeam - DS.Spacing.homeCardSpacing)
        }
        // The badge morph's source width: `HomeView` publishes this view's
        // bounds through `HomeBadgeSourceFrameKey`.
        .frame(maxWidth: .infinity)
    }

    // MARK: Monthly mode

    private func monthlyContent(
        progress: BadgeHeroState.MonthlyProgress, chosen: BadgeRef?, now: Date
    ) -> some View {
        let total = progress.baseSeconds
            + (progress.isLive ? liveReclaimed.badgeLiveTailSeconds(now: now, inMonth: progress.monthKey) : 0)
        let tier = BadgeConfig.displayTier(
            forMonthSeconds: total, daysInMonth: progress.daysInMonth,
            notBelow: progress.floorTier
        )
        // The DISPLAYED tier drives everything below: the title (the tier
        // held), the line's next tier and amount, and the bar all swap together
        // at the choreography's promote beat. The `??` covers the first render
        // before `.onAppear` seeds the latch.
        let shownTier = displayedTier ?? tier
        // Only the badge and the title use this one; the bar and the line keep
        // describing the real tier. With a choice set (the user's, or
        // Automatic's newer badge) it is that badge, so a promotion changes
        // neither the badge nor the title.
        let homeBadge = shownBadge(realTier: shownTier, chosen: chosen)
        // One frozen value behind the bar and the line, so they cannot
        // disagree. It is pinned to the SHOWN tier, not the computed one, which
        // is what keeps them describing a single segment through the promotion
        // beats.
        let segment = BadgeConfig.segmentProgress(
            forMonthSeconds: total, daysInMonth: progress.daysInMonth, pinnedTier: shownTier
        )
        // The line says "this month" whenever Home's badge is not this month's
        // tier, because the title then no longer names it. A Debug preview
        // counts as showing the month's tier: it stands in for the real one.
        let homeBadgeIsShownTier = isBadgePreviewActive || chosen == nil
            || chosen == .tier(shownTier)
        let line = BadgeStatePresenter.monthlyHeroLine(
            segment: segment, monthTotalSeconds: total, homeBadgeIsShownTier: homeBadgeIsShownTier
        )
        // The month's next tier is built ahead of time whatever Home shows, so
        // its first crossing loads warm. `progress.floorTier` is the PUBLISHED
        // month tier: never use the live `tier` or `shownTier` for it.
        let nextTierToWarm = BadgeStatePresenter.monthlyTierToWarm(
            shownTier: shownTier, monthTier: progress.floorTier,
            homeBadgeIsShownTier: homeBadgeIsShownTier
        )

        return VStack(spacing: 0) {
            // ZStack: both badge slots share the same fixed footprint during
            // the crossfade, so the promotion cannot shift layout.
            ZStack {
                // The badge the title names: the tier HELD (never the next
                // one) unless the user chose another or Automatic shows a
                // newer badge. The live 3D coin for a tier that has one, its
                // flat art on the same stage for every other badge.
                Badge3DSlot(badge: homeBadge, nextTierToWarm: nextTierToWarm)
                    .id(Badge3DModels.datasetName(for: homeBadge))
                    .transition(
                        reduceMotion
                            ? .opacity
                            : .asymmetric(
                                insertion: .scale(scale: 0.92).combined(with: .opacity),
                                removal: .opacity
                            )
                    )
            }
            .opensAllBadges(perform: onSeeAll)
            .padding(.top, Badge3DLayout.slotTopPadding)
            .animation(Animations.tierPromotionSwap, value: homeBadge)
            heroTitle("You earned \(BadgeStatePresenter.homeBadgeName(homeBadge))")
                .contentTransition(.opacity)
                .animation(Animations.tierPromotionSwap, value: homeBadge)
                .padding(.top, Self.titleTopPadding)
            monthlyLineText(line)
                // Rolls once per minute as the time left (or, at the top
                // tier, the month's total) changes. Below the top tier the
                // time left only shrinks, so it rolls down; at the top the
                // month's hours only grow, so it rolls up. Reduce Motion
                // crossfades. The roll is off while a promotion runs, so the
                // reset snaps while the line is faded out.
                .contentTransition(
                    reduceMotion ? .opacity : .numericText(countsDown: segment.next != nil)
                )
                .animation(promotionInFlight ? nil : Animations.heroCounter, value: line)
                .opacity(promotionBarOpacity)
                .animation(Animations.tierPromotionBarFade, value: promotionBarOpacity)
                .padding(.top, Self.titleToLineGap)
            HomeBadgeProgressBar(fraction: segment.fraction)
                .opacity(promotionBarOpacity)
                .animation(Animations.tierPromotionBarFade, value: promotionBarOpacity)
                .padding(.top, Self.lineToBarGap)
            #if DEBUG
            badgePreviewRow
            #endif
        }
        .onAppear {
            // Seed the latch without any animation so a cold appearance
            // never plays a promotion.
            if displayedTier == nil { displayedTier = tier }
        }
        .onChange(of: tier) { _, newTier in
            handleComputedTierChange(to: newTier)
        }
    }

    /// Applies a computed-tier change to the displayed tier. A promotion
    /// runs the quiet two-beat choreography; a demotion (the month rollover
    /// resets the climb) or an equal-tier refresh just tracks the value.
    /// Crossing a tier is one of the few genuinely earned moments on Home:
    /// without this, the badge art hard-swaps and the full progress bar
    /// collapses to empty in one frame, which reads as loss. The exuberant
    /// version stays where it already lives (the full-screen
    /// BadgeCelebrationFlowView, presented separately); the hero only
    /// acknowledges.
    private func handleComputedTierChange(to newTier: MonthlyTier) {
        guard let shown = displayedTier else {
            displayedTier = newTier
            return
        }
        // Mid-choreography ticks are ignored: the run already targets the
        // latest crossing, and monthly tiers are hours of reclaimed time
        // apart, so a second crossing cannot land inside one ~0.85s run.
        guard !promotionInFlight else { return }
        guard Self.tierRank(newTier) > Self.tierRank(shown) else {
            displayedTier = newTier
            return
        }
        guard !reduceMotion else {
            // Reduce Motion: promote instantly. The badge still crossfades
            // via its .opacity transition; the bar snaps.
            displayedTier = newTier
            return
        }
        promotionInFlight = true
        Task { @MainActor in
            // Beat 1: hold. On the crossing tick the segment fraction
            // clamps at the ceiling, so the bar is already sitting at 100%
            // (and the line reads "1 more minute", the amount's floor, for
            // this beat); let the full bar register before anything moves.
            try? await Task.sleep(for: .milliseconds(350))
            // Beat 2: the full bar and the line bow out.
            promotionBarOpacity = 0
            try? await Task.sleep(for: .milliseconds(200))
            // Beat 3, promote: badge art and title crossfade via their
            // tierPromotionSwap animations; the invisible bar and line snap to
            // the new segment at the same instant.
            displayedTier = newTier
            try? await Task.sleep(for: .milliseconds(120))
            // Beat 4: the fresh climb fades in.
            promotionBarOpacity = 1
            promotionInFlight = false
        }
    }

    /// Ladder rank (iron < … < diamond). `MonthlyTier` is not Comparable;
    /// `BadgeConfig.tierIndex` (the ladder's single order authority) gives
    /// the 1-based position, which is all a promotion comparison needs.
    private static func tierRank(_ tier: MonthlyTier) -> Int {
        BadgeConfig.tierIndex(tier)
    }

    /// The monthly line, styled: the words around the figures quiet, the amount
    /// and the tier being climbed toward emphasized, like achievement mode's
    /// "Next: " line. VoiceOver reads the runs as one plain sentence.
    private func monthlyLineText(_ line: MonthlyHeroLine) -> some View {
        var lineText = Text(verbatim: "")
        for run in line.runs {
            lineText = lineText + runText(run)
        }
        return centeredLine(lineText)
    }

    private func runText(_ run: MonthlyHeroLine.Run) -> Text {
        guard run.isEmphasized else {
            return Text(run.text).foregroundStyle(DS.Colors.textSecondary)
        }
        // Monospaced digits keep a digit change in the rolling amount from
        // rewrapping the centered sentence. Tier names have no digits, so
        // this leaves them as they were.
        return emphasized(Text(run.text)).monospacedDigit()
    }

    // MARK: Badge preview (Debug only)

    /// The badge Home shows in monthly mode: the Debug preview's tier while
    /// there is one, else the user's choice or Automatic's override (the newest
    /// badge, only while `BadgeConfig.homeBadgeIsMonthlyOnly` is off), else the
    /// real tier held. Release builds have no preview.
    private func shownBadge(realTier: MonthlyTier, chosen: BadgeRef?) -> BadgeRef {
        #if DEBUG
        if let previewTier { return .tier(previewTier) }
        #endif
        return chosen ?? .tier(realTier)
    }

    /// Whether the Debug preview is standing in for the real badge. Always
    /// false in Release.
    private var isBadgePreviewActive: Bool {
        #if DEBUG
        return previewTier != nil
        #else
        return false
        #endif
    }

    #if DEBUG
    /// "BADGE PREVIEW" on the left and the button that steps through the
    /// ladder on the right, under the real progress bar so the layout above
    /// never moves.
    private var badgePreviewRow: some View {
        HStack {
            Text("Badge preview").foregroundStyle(DS.Colors.textSecondary).heroCapsStyle(weight: .semibold)
            Spacer()
            Menu {
                ForEach(PrivateBadgePreview.items.keys.sorted(), id: \.self) { key in
                    Button(PrivateBadgePreview.items[key] ?? key) {
                        previewCoin = key
                        PrivateBadgePreview.selection = key
                        UserDefaults.standard.set(key, forKey: "CoinBadgePreview")
                        previewTier = .silver
                    }
                }
                Divider()
                ForEach(MonthlyTier.allCases, id: \.self) { tier in
                    Button(tier.displayName) {
                        previewCoin = ""
                        PrivateBadgePreview.selection = ""
                        UserDefaults.standard.set("", forKey: "CoinBadgePreview")
                        previewTier = tier
                    }
                }
            } label: {
                Text("Choose badge").foregroundStyle(DS.Colors.accent).heroCapsStyle(weight: .bold).frame(minHeight: Self.linkTouchHeight)
            }
            .accessibilityIdentifier("coinPreviewPicker")
        }.padding(.top, 16)
    }

    /// The next stop in the preview cycle: nothing goes to the first tier,
    /// each tier goes to the one above it, and the top tier goes back to
    /// nothing (the real badge).
    private static func previewTier(after currentTier: MonthlyTier?) -> MonthlyTier? {
        let ladder = MonthlyTier.allCases
        guard let currentTier else { return ladder.first }
        guard let currentIndex = ladder.firstIndex(of: currentTier),
            currentIndex + 1 < ladder.count
        else { return nil }
        return ladder[currentIndex + 1]
    }
    #endif

    // MARK: Achievement mode

    private func achievementContent(
        hero: BadgeHeroState, chosen: BadgeRef?, nextTierToWarm: MonthlyTier?
    ) -> some View {
        let homeBadge = chosen ?? hero.badge
        let title = chosen.map(BadgeStatePresenter.homeBadgeName) ?? hero.name
        return VStack(spacing: 0) {
            // The badge is always one the user has already EARNED (the newest
            // earned badge while `BadgeConfig.homeBadgeIsMonthlyOnly` is off, or
            // their choice), so it draws in the default earned
            // metal art: the live 3D coin for a tier that has one, flat on the
            // same lit stage for any other badge. It sits deliberately OUTSIDE
            // the `if let` below: a missing line must never blank the art.
            //
            // Keyed on the 3D model's name, not on the badge: the slot keeps
            // per-model scene state, so it must be rebuilt exactly when a swap
            // moves to, from or between 3D models. A flat-to-flat swap (a new
            // achievement) keeps the same slot, so it stays as instant as it
            // always was. No transition: achievement mode never animated.
            Badge3DSlot(badge: homeBadge, nextTierToWarm: nextTierToWarm)
                .id(Badge3DModels.datasetName(for: homeBadge))
                .opensAllBadges(perform: onSeeAll)
                .padding(.top, Badge3DLayout.slotTopPadding)
            heroTitle("You earned \(title)")
                .padding(.top, Self.titleTopPadding)
            if let line = hero.achievementLine {
                centeredLine(achievementLineText(line))
                    .padding(.top, Self.titleToLineGap)
                    // VoiceOver reads the rung as the label and the progress,
                    // in spoken durations, as the value, so it never says
                    // "10m of 1h" literally.
                    .accessibilityElement(children: .ignore)
                    .accessibilityLabel(line.text)
                    .accessibilityValue(line.spokenProgressLabel ?? "")
                // All earned: the presenter's fraction is 1, a full bar.
                HomeBadgeProgressBar(fraction: line.fraction)
                    .padding(.top, Self.lineToBarGap)
            }
        }
    }

    /// The line in achievement mode: the rung ("Next: 1 Hour Blocked") and,
    /// while there is a climb to describe, a quiet separator and how far it has
    /// come ("10m of 1h").
    private func achievementLineText(_ line: BadgeHeroState.AchievementLine) -> Text {
        guard let progressLabel = line.progressLabel else {
            return achievementRowTitle(line)
        }
        return achievementRowTitle(line)
            + Text(" · ").foregroundStyle(DS.Colors.textSecondary)
            + progressLabelText(progressLabel)
    }

    /// The rung in achievement mode: "Next: " quiet and the rung's name
    /// emphasized, or the completion line once every rung is earned.
    private func achievementRowTitle(_ line: BadgeHeroState.AchievementLine) -> Text {
        guard let nextName = line.nextName else {
            return Text(line.text).foregroundStyle(DS.Colors.textSecondary)
        }
        return Text("Next: ").foregroundStyle(DS.Colors.textSecondary)
            + emphasized(Text(nextName))
    }

    // MARK: Shared pieces

    /// The title under the badge: "You earned <name>", the mock's 30pt heavy
    /// title (32pt drew it 6% wider than the mock against the badge), centered. A long achievement name ("Start of the Journey") wraps
    /// onto a second line, and shrinks a little if it still does not fit,
    /// rather than truncating.
    private func heroTitle(_ text: String) -> some View {
        Text(PrivateBadgePreview.items[previewCoin] ?? text)
            .font(.system(size: 30, weight: .heavy))
            .kerning(-0.8)
            .foregroundStyle(BadgeHeroPalette.primary)
            .multilineTextAlignment(.center)
            .lineLimit(2)
            .minimumScaleFactor(0.7)
            .frame(maxWidth: .infinity)
    }

    /// The line's look in both modes: 17pt regular, centered, at most two
    /// lines (the longest monthly line wraps on a 375pt phone), full width.
    private func centeredLine(_ text: Text) -> some View {
        text
            .font(.system(size: 17, weight: .regular))
            .multilineTextAlignment(.center)
            .lineLimit(2)
            .frame(maxWidth: .infinity)
    }

    /// Achievement mode's progress label ("10m of 1h", "5 of 7 days"). The
    /// presenter hands it over as one string, so it is split at " of " to
    /// emphasize its first quantity. A label with no " of " has no climb to
    /// single out, so it stays quiet throughout.
    private func progressLabelText(_ label: String) -> Text {
        guard let ofRange = label.range(of: " of ") else {
            return Text(label).foregroundStyle(DS.Colors.textSecondary)
        }
        let climbed = String(label[..<ofRange.lowerBound])
        let remainder = String(label[ofRange.lowerBound...])
        return emphasizedFigureLabel(figure: climbed, remainder: remainder)
    }

    /// A progress label that leads with the number that grows ("10m" in
    /// "10m of 1h"): that figure emphasized, the words after it quiet.
    private func emphasizedFigureLabel(figure: String, remainder: String) -> Text {
        emphasized(Text(figure))
            + Text(remainder).foregroundStyle(DS.Colors.textSecondary)
    }

    /// A run of the line the eye should land on first (the amount, the tier
    /// or rung being climbed toward): brighter and heavier than the quiet words
    /// around it, like the mock's bold runs.
    private func emphasized(_ text: Text) -> Text {
        text
            .fontWeight(.bold)
            .foregroundStyle(BadgeHeroPalette.primary)
    }

    /// The standard 44pt touch height of the Debug preview's button.
    private static let linkTouchHeight: CGFloat = 44

    /// The three gaps under the badge, tuned so they keep the 2026-10-25 Home
    /// mock's proportions to the badge's width. The title's gap is slightly
    /// negative: the slot's frame runs a little past the badge's reflection, and
    /// the title's own top inset keeps its letters clear of the badge.
    private static let titleTopPadding: CGFloat = -1
    private static let titleToLineGap: CGFloat = 13.5
    private static let lineToBarGap: CGFloat = 18
}

/// Home's progress bar: a 10pt capsule on a near black track, filled with a
/// gray to white gradient that runs across the fill's own width, so even a
/// short fill ends in white. The tier sheet keeps `HeroProgressBar`.
private struct HomeBadgeProgressBar: View {
    let fraction: Double

    private static let height: CGFloat = 10
    // Sampled from the 2026-10-25 Home mock.
    private static let trackColor = Color(red: 0x1C / 255, green: 0x1C / 255, blue: 0x1E / 255)
    private static let fillStartColor = Color(red: 0x8F / 255, green: 0x91 / 255, blue: 0x97 / 255)
    private static let fillEndColor = Color(red: 0xE8 / 255, green: 0xEA / 255, blue: 0xEE / 255)

    var body: some View {
        // ONE layout GeometryReader: `proxy.size.width` is the track width,
        // right on the first frame with no state involved. The explicit height
        // is load-bearing: without it the reader takes all the height its
        // VStack offers.
        GeometryReader { proxy in
            ZStack(alignment: .leading) {
                Capsule().fill(Self.trackColor)
                Capsule()
                    .fill(
                        LinearGradient(
                            colors: [Self.fillStartColor, Self.fillEndColor],
                            startPoint: .leading,
                            endPoint: .trailing
                        )
                    )
                    .frame(width: proxy.size.width * clampedFraction)
            }
        }
        .frame(height: Self.height)
        // The line above the bar already says the same thing.
        .accessibilityHidden(true)
    }

    private var clampedFraction: Double {
        min(1, max(0, fraction))
    }
}

private extension View {
    /// Makes the badge the one control that opens the All badges layer. A tap
    /// gesture, never a `Button`: a plain button dims its whole label while
    /// pressed, and the badge's label holds the lit stage, which spills past
    /// the slot on every side, so every press would dim the stage. VoiceOver
    /// gets one "All badges" button, with an explicit action so a double tap
    /// opens it for certain.
    func opensAllBadges(perform openAllBadges: @escaping () -> Void) -> some View {
        self
            .contentShape(BadgeTapArea())
            .onTapGesture(perform: openAllBadges)
            .accessibilityElement(children: .ignore)
            .accessibilityLabel("All badges")
            .accessibilityAddTraits(.isButton)
            .accessibilityAction { openAllBadges() }
    }
}

/// The badge slot's tap area: the slot's frame, minus a strip along the bottom.
/// The title sits right under the slot (its gap is slightly negative), and a
/// tap lands up to about 10pt outside a view's frame (measured on the
/// simulator, where taps just under the slot still opened the layer). The
/// strip holds only the badge's faint reflection, and keeping it out of the tap
/// area leaves the title's letters to do nothing, as the plan says.
private struct BadgeTapArea: Shape {
    private static let bottomStripHeight: CGFloat = 12

    func path(in rect: CGRect) -> Path {
        Path(CGRect(
            x: rect.minX, y: rect.minY,
            width: rect.width, height: max(0, rect.height - Self.bottomStripHeight)
        ))
    }
}

// MARK: - Previews

#Preview("Monthly climber") {
    NavigationStack {
        ScrollView {
            BadgeHeroCard(onSeeAll: {})
                .padding(.horizontal, 20)
        }
        .background(DS.Colors.pageBackground)
    }
    .environment(\.badges, MockBadgeViewModel(.midMonthClimber))
}

#Preview("Day one") {
    NavigationStack {
        ScrollView {
            BadgeHeroCard(onSeeAll: {})
                .padding(.horizontal, 20)
        }
        .background(DS.Colors.pageBackground)
    }
    .environment(\.badges, MockBadgeViewModel(.dayOne))
}

#Preview("Pre-monthly") {
    NavigationStack {
        ScrollView {
            BadgeHeroCard(onSeeAll: {})
                .padding(.horizontal, 20)
        }
        .background(DS.Colors.pageBackground)
    }
    .environment(\.badges, MockBadgeViewModel(.preMonthly))
}

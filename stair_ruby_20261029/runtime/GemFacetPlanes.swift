import Foundation

/// Turns a gem's triangles into its distinct outward facet planes: the data the
/// Diamond's gem shader traces light through (`BadgeGemSurface.metal`). For a
/// convex gem a ray inside leaves through the first facet plane it reaches, so
/// a short list of planes is all the shader needs, instead of every triangle.
///
/// Kept free of RealityKit and SwiftUI so it can be unit-tested directly.
enum GemFacetPlanes {
    /// The most planes the shader looks through per pixel. A model with more
    /// facets than this is too costly to trace on the phone, so it is refused.
    static let maximumPlaneCount = 256

    /// The distinct outward planes of the closed convex gem made of `corners`
    /// (every three consecutive corners are one triangle), each as
    /// (normal x, normal y, normal z, offset): a point `p` is on the plane when
    /// `normal . p = offset`, and inside the gem when `normal . p < offset`.
    ///
    /// Nil when `corners` is not a whole number of triangles, when there are
    /// fewer than 4 or more than `maximumPlaneCount` planes, or when any corner
    /// lies more than `tolerance` outside any plane (the gem has a dent, so
    /// the shader's "leave through the first plane" trace would be wrong).
    ///
    /// Each normal points away from the centroid of all corners, never from
    /// the triangle's winding: the mirror image under the floor has its
    /// winding reversed. Triangles with no area are skipped, and planes whose
    /// normals and offsets agree within `tolerance` are one plane (the
    /// triangles of one facet, or of two facets too close to tell apart).
    static func outwardPlanes(
        ofTriangles corners: [SIMD3<Float>],
        tolerance: Float = 0.001
    ) -> [SIMD4<Float>]? {
        guard !corners.isEmpty, corners.count % 3 == 0 else { return nil }
        let centroid = centroid(of: corners)

        var planes: [SIMD4<Float>] = []
        for firstCorner in stride(from: 0, to: corners.count, by: 3) {
            guard let plane = outwardPlane(
                throughTriangleStartingAt: firstCorner, in: corners, awayFrom: centroid
            ) else { continue }
            if !planes.contains(where: { isSamePlane($0, plane, tolerance: tolerance) }) {
                planes.append(plane)
            }
            // A smooth model has a plane per triangle: stop before comparing
            // thousands of them with each other.
            if planes.count > maximumPlaneCount { return nil }
        }

        guard planes.count >= 4 else { return nil }
        guard isEveryCorner(of: corners, insideOrOn: planes, tolerance: tolerance) else { return nil }
        return planes
    }

    // MARK: Steps

    private static func centroid(of corners: [SIMD3<Float>]) -> SIMD3<Float> {
        corners.reduce(SIMD3<Float>.zero, +) / Float(corners.count)
    }

    /// The plane of one triangle with its normal turned away from `centroid`,
    /// or nil when the triangle has (almost) no area.
    private static func outwardPlane(
        throughTriangleStartingAt firstCorner: Int,
        in corners: [SIMD3<Float>],
        awayFrom centroid: SIMD3<Float>
    ) -> SIMD4<Float>? {
        let first = corners[firstCorner]
        let second = corners[firstCorner + 1]
        let third = corners[firstCorner + 2]
        let areaVector = crossProduct(second - first, third - first)
        let doubleArea = dotProduct(areaVector, areaVector).squareRoot()
        // Half the length of the cross product is the triangle's area.
        guard doubleArea / 2 >= 1e-10 else { return nil }

        var normal = areaVector / doubleArea
        var offset = dotProduct(normal, first)
        if dotProduct(normal, centroid) > offset {
            normal = -normal
            offset = -offset
        }
        return SIMD4(normal.x, normal.y, normal.z, offset)
    }

    private static func isSamePlane(_ a: SIMD4<Float>, _ b: SIMD4<Float>, tolerance: Float) -> Bool {
        let difference = a - b
        return abs(difference.x) <= tolerance
            && abs(difference.y) <= tolerance
            && abs(difference.z) <= tolerance
            && abs(difference.w) <= tolerance
    }

    private static func isEveryCorner(
        of corners: [SIMD3<Float>],
        insideOrOn planes: [SIMD4<Float>],
        tolerance: Float
    ) -> Bool {
        for corner in corners {
            for plane in planes {
                let normal = SIMD3(plane.x, plane.y, plane.z)
                if dotProduct(normal, corner) - plane.w > tolerance { return false }
            }
        }
        return true
    }

    // The Swift standard library has no dot or cross product for SIMD vectors
    // (they live in the `simd` module, which this file does not import).

    private static func dotProduct(_ a: SIMD3<Float>, _ b: SIMD3<Float>) -> Float {
        (a * b).sum()
    }

    private static func crossProduct(_ a: SIMD3<Float>, _ b: SIMD3<Float>) -> SIMD3<Float> {
        SIMD3(
            a.y * b.z - a.z * b.y,
            a.z * b.x - a.x * b.z,
            a.x * b.y - a.y * b.x
        )
    }
}

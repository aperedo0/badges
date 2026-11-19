import Foundation
import CoreGraphics
let windows = CGWindowListCopyWindowInfo([.optionOnScreenOnly, .excludeDesktopElements], kCGNullWindowID) as? [[String: Any]] ?? []
for window in windows {
 if (window[kCGWindowOwnerName as String] as? String) == "Blender", (window[kCGWindowLayer as String] as? Int) == 0 {
  let result: [String: Any] = ["id": window[kCGWindowNumber as String] ?? 0, "title": window[kCGWindowName as String] ?? "", "bounds": window[kCGWindowBounds as String] ?? [:]]
  if let data = try? JSONSerialization.data(withJSONObject: result), let text = String(data: data, encoding: .utf8) { print(text) }
 }
}

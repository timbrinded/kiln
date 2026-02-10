# Deprecated API Replacement Guide

The #1 failure mode in AI-generated SwiftUI: defaulting to pre-iOS 17 patterns. This guide provides before/after replacements for every commonly misused API.

Default target: **iOS 17+**. Rules marked iOS 18+ become suggestions when targeting iOS 17.

---

## Navigation (iOS 16+)

### NavigationView → NavigationStack

**Deprecated:**
```swift
NavigationView {
    List(items) { item in
        NavigationLink(destination: DetailView(item: item)) {
            Text(item.name)
        }
    }
    .navigationTitle("Items")
}
```

**Modern:**
```swift
NavigationStack {
    List(items) { item in
        NavigationLink(value: item) {
            Text(item.name)
        }
    }
    .navigationTitle("Items")
    .navigationDestination(for: Item.self) { item in
        DetailView(item: item)
    }
}
```

**Why it matters:** `NavigationStack` supports value-based navigation, deep linking, and programmatic path manipulation via `NavigationPath`. `NavigationView` has undefined behavior with `TabView`.

### NavigationView with columns → NavigationSplitView

**Deprecated:**
```swift
NavigationView {
    SidebarView()
    DetailView()
}
```

**Modern:**
```swift
NavigationSplitView {
    SidebarView()
} detail: {
    DetailView()
}
```

---

## Observation (iOS 17+)

### ObservableObject → @Observable

**Deprecated:**
```swift
class UserViewModel: ObservableObject {
    @Published var name: String = ""
    @Published var email: String = ""
    @Published var isLoading: Bool = false
}

struct UserView: View {
    @StateObject private var viewModel = UserViewModel()
    // or
    @ObservedObject var viewModel: UserViewModel
    // or
    @EnvironmentObject var viewModel: UserViewModel

    var body: some View {
        Text(viewModel.name)
    }
}
```

**Modern:**
```swift
@Observable
class UserViewModel {
    var name: String = ""
    var email: String = ""
    var isLoading: Bool = false
}

struct UserView: View {
    @State private var viewModel = UserViewModel()
    // or for injected:
    var viewModel: UserViewModel
    // or for environment:
    @Environment(UserViewModel.self) var viewModel

    var body: some View {
        Text(viewModel.name)
    }
}
```

**Why it matters:** `@Observable` uses property-level observation — views only re-render when the specific properties they read change. `ObservableObject` triggers re-renders on ANY `@Published` property change, causing unnecessary work.

### Property wrapper mapping

| Old | New | Usage |
|-----|-----|-------|
| `@StateObject` | `@State` | View owns the object |
| `@ObservedObject` | Direct property (no wrapper) | Injected from parent |
| `@EnvironmentObject` | `@Environment(Type.self)` | Injected via environment |
| `@Published` | Plain `var` (inside `@Observable`) | Observable property |

---

## TabView (iOS 18+)

### .tabItem() → Tab API

**Deprecated:**
```swift
TabView {
    HomeView()
        .tabItem {
            Label("Home", systemImage: "house")
        }
    SettingsView()
        .tabItem {
            Label("Settings", systemImage: "gear")
        }
}
```

**Modern (iOS 18+):**
```swift
TabView {
    Tab("Home", systemImage: "house") {
        NavigationStack {
            HomeView()
        }
    }
    Tab("Settings", systemImage: "gear") {
        NavigationStack {
            SettingsView()
        }
    }
}
```

**Note:** `.tabItem()` still works and is not formally deprecated. For iOS 17 targets, `.tabItem()` is acceptable. The new `Tab` API adds support for tab customization, sidebar representation on iPad, and better type safety.

---

## View Modifiers (iOS 15+)

### .foregroundColor() → .foregroundStyle()

**Deprecated:**
```swift
Text("Hello")
    .foregroundColor(.blue)

Image(systemName: "star")
    .foregroundColor(.yellow)
```

**Modern:**
```swift
Text("Hello")
    .foregroundStyle(.blue)

Image(systemName: "star")
    .foregroundStyle(.yellow)

// Bonus: foregroundStyle supports gradients and materials
Text("Gradient")
    .foregroundStyle(.linearGradient(colors: [.blue, .purple], startPoint: .leading, endPoint: .trailing))
```

### .background(Color) → .background { } or .background(in:)

**Deprecated:**
```swift
Text("Hello")
    .background(Color.blue)
```

**Modern:**
```swift
Text("Hello")
    .background(.blue)
// or with shape:
Text("Hello")
    .background(.blue, in: RoundedRectangle(cornerRadius: 8))
```

---

## SF Symbols Sizing

### .resizable() → .font() / .imageScale()

**Incorrect:**
```swift
Image(systemName: "star.fill")
    .resizable()
    .frame(width: 24, height: 24)
```

**Correct:**
```swift
Image(systemName: "star.fill")
    .font(.title2)
// or
Image(systemName: "star.fill")
    .imageScale(.large)
// or when precise size is needed:
Image(systemName: "star.fill")
    .font(.system(size: 24))
```

**Why it matters:** SF Symbols are designed to align with text. Using `.font()` ensures they scale with Dynamic Type and maintain proper baseline alignment. `.resizable()` breaks this relationship.

---

## Environment (iOS 18+)

### Custom EnvironmentKey → @Entry macro

**Old pattern:**
```swift
private struct ThemeKey: EnvironmentKey {
    static let defaultValue: Theme = .default
}

extension EnvironmentValues {
    var theme: Theme {
        get { self[ThemeKey.self] }
        set { self[ThemeKey.self] = newValue }
    }
}
```

**Modern (iOS 18+):**
```swift
extension EnvironmentValues {
    @Entry var theme: Theme = .default
}
```

---

## Async Patterns (iOS 15+)

### Completion handlers → async/await

**Old pattern:**
```swift
func fetchUser(completion: @escaping (Result<User, Error>) -> Void) {
    URLSession.shared.dataTask(with: url) { data, response, error in
        // ...
    }.resume()
}
```

**Modern:**
```swift
func fetchUser() async throws -> User {
    let (data, _) = try await URLSession.shared.data(from: url)
    return try JSONDecoder().decode(User.self, from: data)
}
```

**In views:**
```swift
// Old
.onAppear { viewModel.loadData() }

// Modern
.task { await viewModel.loadData() }
```

`.task` automatically cancels when the view disappears — no manual cancellation needed.

---

## Responsive Layout (iOS 16+/17+)

### GeometryReader → Modern alternatives

**Old pattern (measuring container):**
```swift
GeometryReader { proxy in
    Image("hero")
        .resizable()
        .frame(width: proxy.size.width, height: proxy.size.width * 0.6)
}
```

**Modern (iOS 17+):**
```swift
Image("hero")
    .resizable()
    .containerRelativeFrame(.horizontal) { width, _ in
        width
    }
    .aspectRatio(5/3, contentMode: .fit)
```

**Old pattern (adaptive layout):**
```swift
GeometryReader { proxy in
    if proxy.size.width > 500 {
        HStack { content }
    } else {
        VStack { content }
    }
}
```

**Modern (iOS 16+):**
```swift
ViewThatFits(in: .horizontal) {
    HStack { content }
    VStack { content }
}
```

---

## Quick Reference Table

| Deprecated | Replacement | Since |
|------------|-------------|-------|
| `NavigationView` | `NavigationStack` / `NavigationSplitView` | iOS 16 |
| `ObservableObject` | `@Observable` | iOS 17 |
| `@Published` | Plain `var` in `@Observable` class | iOS 17 |
| `@StateObject` | `@State` (with `@Observable`) | iOS 17 |
| `@ObservedObject` | Direct property reference | iOS 17 |
| `@EnvironmentObject` | `@Environment(Type.self)` | iOS 17 |
| `.foregroundColor()` | `.foregroundStyle()` | iOS 15 |
| `.background(Color)` | `.background(shape)` / `.background { }` | iOS 15 |
| `.tabItem { }` | `Tab("", systemImage:) { }` | iOS 18 |
| `EnvironmentKey` boilerplate | `@Entry` macro | iOS 18 |
| Completion handlers | `async/await` + `.task` | iOS 15 |
| `GeometryReader` (sizing) | `containerRelativeFrame` | iOS 17 |
| `GeometryReader` (adaptive) | `ViewThatFits` | iOS 16 |
| `.resizable()` on SF Symbols | `.font()` / `.imageScale()` | Always |

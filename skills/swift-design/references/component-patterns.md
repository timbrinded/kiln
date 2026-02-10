# SwiftUI Component Patterns

Correct structural patterns for the most commonly misused SwiftUI components. Every pattern assumes iOS 17+ unless noted.

---

## TabView + NavigationStack

The single most common structural mistake: wrapping `NavigationStack` around `TabView`. This causes the tab bar to disappear during navigation.

### Correct Pattern

```swift
struct ContentView: View {
    var body: some View {
        TabView {
            Tab("Home", systemImage: "house") {
                NavigationStack {
                    HomeView()
                        .navigationTitle("Home")
                        .navigationBarTitleDisplayMode(.large)
                }
            }
            Tab("Search", systemImage: "magnifyingglass") {
                NavigationStack {
                    SearchView()
                        .navigationTitle("Search")
                }
            }
            Tab("Profile", systemImage: "person") {
                NavigationStack {
                    ProfileView()
                        .navigationTitle("Profile")
                }
            }
        }
    }
}
```

### Common Mistakes

```swift
// WRONG: NavigationStack wrapping TabView
NavigationStack {
    TabView {
        HomeView().tabItem { Label("Home", systemImage: "house") }
    }
}
// Result: Tab bar disappears when pushing views

// WRONG: Single NavigationStack for all tabs
TabView {
    NavigationStack {
        HomeView()
    }
    .tabItem { Label("Home", systemImage: "house") }
}
// Result: Tabs share navigation state — switching tabs doesn't maintain per-tab stack
```

### iOS 17 Pattern (using .tabItem)

```swift
TabView {
    NavigationStack {
        HomeView()
    }
    .tabItem { Label("Home", systemImage: "house") }

    NavigationStack {
        SearchView()
    }
    .tabItem { Label("Search", systemImage: "magnifyingglass") }
}
```

---

## NavigationStack

### Basic Push Navigation

```swift
struct ItemListView: View {
    let items: [Item]

    var body: some View {
        NavigationStack {
            List(items) { item in
                NavigationLink(value: item) {
                    ItemRow(item: item)
                }
            }
            .navigationTitle("Items")
            .navigationBarTitleDisplayMode(.large)
            .navigationDestination(for: Item.self) { item in
                ItemDetailView(item: item)
            }
        }
    }
}
```

### Programmatic Navigation

```swift
struct AppNavigation: View {
    @State private var path = NavigationPath()

    var body: some View {
        NavigationStack(path: $path) {
            HomeView(path: $path)
                .navigationDestination(for: Route.self) { route in
                    switch route {
                    case .detail(let item):
                        ItemDetailView(item: item)
                    case .settings:
                        SettingsView()
                    }
                }
        }
    }
}

enum Route: Hashable {
    case detail(Item)
    case settings
}
```

### Title Display Modes

```swift
// Root screens — large title
.navigationBarTitleDisplayMode(.large)

// Pushed screens — inline title
.navigationBarTitleDisplayMode(.inline)

// Large title that collapses on scroll (default behavior when .large)
NavigationStack {
    ScrollView {
        content
    }
    .navigationTitle("Feed")
    .navigationBarTitleDisplayMode(.large)
}
```

---

## List & Form

### Standard List

```swift
struct SettingsView: View {
    var body: some View {
        List {
            Section("Account") {
                NavigationLink("Profile", value: Route.profile)
                NavigationLink("Notifications", value: Route.notifications)
            }
            Section("General") {
                Toggle("Dark Mode", isOn: $isDarkMode)
                Picker("Language", selection: $language) {
                    Text("English").tag("en")
                    Text("Spanish").tag("es")
                }
            }
            Section {
                Button("Sign Out", role: .destructive) {
                    signOut()
                }
            }
        }
        .navigationTitle("Settings")
    }
}
```

### Searchable List

```swift
struct ContactsView: View {
    @State private var searchText = ""
    let contacts: [Contact]

    var filteredContacts: [Contact] {
        if searchText.isEmpty { return contacts }
        return contacts.filter { $0.name.localizedCaseInsensitiveContains(searchText) }
    }

    var body: some View {
        List(filteredContacts) { contact in
            ContactRow(contact: contact)
        }
        .searchable(text: $searchText, prompt: "Search contacts")
        .navigationTitle("Contacts")
    }
}
```

### Refreshable List

```swift
List(items) { item in
    ItemRow(item: item)
}
.refreshable {
    await loadItems()
}
```

### Swipe Actions

```swift
List(messages) { message in
    MessageRow(message: message)
        .swipeActions(edge: .trailing) {
            Button(role: .destructive) {
                delete(message)
            } label: {
                Label("Delete", systemImage: "trash")
            }
            Button {
                archive(message)
            } label: {
                Label("Archive", systemImage: "archivebox")
            }
            .tint(.blue)
        }
        .swipeActions(edge: .leading) {
            Button {
                toggleRead(message)
            } label: {
                Label("Read", systemImage: message.isRead ? "envelope" : "envelope.open")
            }
            .tint(.green)
        }
}
```

---

## Alerts & Confirmation Dialogs

### Alert with Roles

```swift
.alert("Delete Item?", isPresented: $showDeleteAlert) {
    Button("Delete", role: .destructive) {
        deleteItem()
    }
    Button("Cancel", role: .cancel) { }
} message: {
    Text("This action cannot be undone.")
}
```

### Confirmation Dialog (Action Sheet Replacement)

```swift
.confirmationDialog("Share Photo", isPresented: $showShareOptions) {
    Button("Save to Photos") { saveToPhotos() }
    Button("Copy Link") { copyLink() }
    Button("Send via Messages") { sendMessage() }
    Button("Delete", role: .destructive) { deletePhoto() }
    Button("Cancel", role: .cancel) { }
} message: {
    Text("Choose how to share this photo")
}
```

**Rule**: Always use `.role(.cancel)` and `.role(.destructive)` — iOS uses these to position buttons correctly per platform convention.

---

## Sheets & Presentation

### Standard Sheet

```swift
.sheet(isPresented: $showCompose) {
    ComposeView()
}

// With item binding
.sheet(item: $selectedItem) { item in
    DetailView(item: item)
}
```

### Sheet with Detents (Half-Height)

```swift
.sheet(isPresented: $showOptions) {
    OptionsView()
        .presentationDetents([.medium, .large])
        .presentationDragIndicator(.visible)
}
```

### Full Screen Cover

```swift
.fullScreenCover(isPresented: $showOnboarding) {
    OnboardingView()
}
```

### Sheet Dismiss Pattern

```swift
struct ComposeView: View {
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        NavigationStack {
            Form { /* ... */ }
                .navigationTitle("New Message")
                .toolbar {
                    ToolbarItem(placement: .cancellationAction) {
                        Button("Cancel") { dismiss() }
                    }
                    ToolbarItem(placement: .confirmationAction) {
                        Button("Send") {
                            send()
                            dismiss()
                        }
                    }
                }
        }
    }
}
```

---

## View Composition

### Extract Subviews at 40–60 Lines

```swift
// Before: monolithic body
struct OrderView: View {
    var body: some View {
        ScrollView {
            // 80+ lines of mixed content...
        }
    }
}

// After: composed from focused subviews
struct OrderView: View {
    var body: some View {
        ScrollView {
            VStack(spacing: 24) {
                OrderHeader(order: order)
                ItemList(items: order.items)
                PricingSummary(order: order)
                ActionButtons(onConfirm: confirm, onCancel: cancel)
            }
            .padding()
        }
    }
}
```

### ViewModifier for Reusable Styling

```swift
struct CardModifier: ViewModifier {
    func body(content: Content) -> some View {
        content
            .padding(16)
            .background(.background.secondary, in: RoundedRectangle(cornerRadius: 12, style: .continuous))
    }
}

extension View {
    func cardStyle() -> some View {
        modifier(CardModifier())
    }
}

// Usage
Text("Card content").cardStyle()
```

### ButtonStyle for Custom Buttons

```swift
struct PrimaryButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(.headline)
            .foregroundStyle(.white)
            .frame(maxWidth: .infinity, minHeight: 50)
            .background(.accent, in: RoundedRectangle(cornerRadius: 12, style: .continuous))
            .opacity(configuration.isPressed ? 0.8 : 1)
    }
}

// Usage
Button("Continue") { next() }
    .buttonStyle(PrimaryButtonStyle())
```

---

## Empty, Loading, Error States

### Empty State Pattern

```swift
struct EmptyStateView: View {
    let icon: String
    let title: String
    let description: String
    let actionTitle: String?
    let action: (() -> Void)?

    var body: some View {
        ContentUnavailableView {
            Label(title, systemImage: icon)
        } description: {
            Text(description)
        } actions: {
            if let actionTitle, let action {
                Button(actionTitle, action: action)
                    .buttonStyle(.borderedProminent)
            }
        }
    }
}
```

### Loading State

```swift
// Indeterminate
ProgressView()
    .controlSize(.large)

// Skeleton/placeholder
RoundedRectangle(cornerRadius: 8)
    .fill(.quaternary)
    .frame(height: 20)
    .shimmer() // custom modifier
```

### Error State

```swift
ContentUnavailableView {
    Label("Connection Error", systemImage: "wifi.slash")
} description: {
    Text("Check your internet connection and try again.")
} actions: {
    Button("Retry") {
        Task { await retry() }
    }
    .buttonStyle(.borderedProminent)
}
```

---

## @Observable ViewModel Pattern

```swift
@Observable
class ItemListViewModel {
    var items: [Item] = []
    var isLoading = false
    var error: Error?

    func loadItems() async {
        isLoading = true
        defer { isLoading = false }
        do {
            items = try await ItemService.fetchAll()
        } catch {
            self.error = error
        }
    }
}

struct ItemListView: View {
    @State private var viewModel = ItemListViewModel()

    var body: some View {
        Group {
            if viewModel.isLoading {
                ProgressView()
            } else if let error = viewModel.error {
                ErrorView(error: error, retry: { Task { await viewModel.loadItems() } })
            } else if viewModel.items.isEmpty {
                EmptyStateView(icon: "tray", title: "No Items", description: "Add your first item to get started.", actionTitle: "Add Item", action: nil)
            } else {
                List(viewModel.items) { item in
                    ItemRow(item: item)
                }
            }
        }
        .task { await viewModel.loadItems() }
    }
}
```

from .customers import (
    AccountView,
    CustomerStatsView,
    CustomerSubscriptionCreateView,
    DashboardView,
    NotificationsView,
    SubscriptionView,
    WialonLoginView,
)
from .notifications import (
    WialonNotificationCreateSuccessView,
    WialonNotificationCreateView,
    WialonNotificationDeleteView,
    WialonNotificationDetailView,
    WialonNotificationListView,
    WialonNotificationTriggerFormView,
    WialonNotificationTriggerParametersFormView,
    WialonNotificationTriggerParametersSuccessView,
    WialonNotificationUnitSelectFormView,
    WialonNotificationUpdateView,
)
from .packages import (
    MessagePackageCreateView,
    MessagePackageListView,
    MessagePackagePriceView,
)
from .public import (
    ContactView,
    DocumentationView,
    HomeView,
    LoginView,
    LogoutView,
    NavbarView,
    PrivacyView,
    RegisterView,
    SourceCodeView,
    TermsView,
)

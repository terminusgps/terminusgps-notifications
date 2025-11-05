from django.urls import path

from . import views

app_name = "terminusgps_notifications"
urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("navbar/", views.NavbarView.as_view(), name="navbar"),
    path("terms/", views.TermsView.as_view(), name="terms"),
    path("source/", views.SourceCodeView.as_view(), name="source code"),
    path("privacy/", views.PrivacyView.as_view(), name="privacy"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("account/", views.AccountView.as_view(), name="account"),
    path("stats/", views.CustomerStatsView.as_view(), name="stats"),
    path("contact/", views.ContactView.as_view(), name="contact"),
    path(
        "subscription/", views.SubscriptionView.as_view(), name="subscription"
    ),
    path(
        "subscriptions/create/",
        views.CustomerSubscriptionCreateView.as_view(),
        name="create subscriptions",
    ),
    path(
        "notifications/",
        views.NotificationsView.as_view(),
        name="notifications",
    ),
    path(
        "notifications/list/",
        views.WialonNotificationListView.as_view(),
        name="list notifications",
    ),
    path(
        "notifications/create/",
        views.WialonNotificationCreateView.as_view(),
        name="create notifications",
    ),
    path(
        "notifications/create/success/",
        views.WialonNotificationCreateSuccessView.as_view(),
        name="create notifications success",
    ),
    path(
        "notifications/<int:notification_pk>/detail/",
        views.WialonNotificationDetailView.as_view(),
        name="detail notifications",
    ),
    path(
        "notifications/<int:notification_pk>/update/",
        views.WialonNotificationUpdateView.as_view(),
        name="update notifications",
    ),
    path(
        "notifications/<int:notification_pk>/delete/",
        views.WialonNotificationDeleteView.as_view(),
        name="delete notifications",
    ),
    path(
        "notifications/units/form/",
        views.WialonNotificationUnitSelectFormView.as_view(),
        name="units form",
    ),
    path(
        "notifications/triggers/form/",
        views.WialonNotificationTriggerFormView.as_view(),
        name="triggers form",
    ),
    path(
        "notifications/triggers/parameters/form/",
        views.WialonNotificationTriggerParametersFormView.as_view(),
        name="trigger parameters form",
    ),
    path(
        "notifications/triggers/parameters/success/",
        views.WialonNotificationTriggerParametersSuccessView.as_view(),
        name="trigger parameters success",
    ),
    path(
        "wialon/login/", views.WialonLoginView.as_view(), name="wialon login"
    ),
]

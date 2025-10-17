from django.urls import path

from . import views

app_name = "terminusgps_notifications"
urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("stats/", views.CustomerStatsView.as_view(), name="stats"),
    path("account/", views.AccountView.as_view(), name="account"),
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
        "notifications/units/select/",
        views.WialonNotificationUnitSelectFormView.as_view(),
        name="select units",
    ),
    path(
        "notifications/triggers/select/",
        views.WialonNotificationTriggerSelectFormView.as_view(),
        name="select triggers",
    ),
    path(
        "notifications/triggers/parameters/",
        views.WialonNotificationTriggerParametersFormView.as_view(),
        name="trigger parameters",
    ),
    path(
        "notifications/triggers/parameters/success/",
        views.WialonNotificationTriggerParametersFormSuccessView.as_view(),
        name="trigger parameters success",
    ),
    path(
        "wialon/login/", views.WialonLoginView.as_view(), name="wialon login"
    ),
    path(
        "wialon/callback/",
        views.WialonCallbackView.as_view(),
        name="wialon callback",
    ),
]

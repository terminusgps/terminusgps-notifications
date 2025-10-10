from django.urls import path

from . import views

app_name = "terminusgps_notifications"
urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path(
        "wialon/login/", views.WialonLoginView.as_view(), name="wialon login"
    ),
    path(
        "wialon/<int:customer_pk>/callback/",
        views.WialonCallbackView.as_view(),
        name="wialon callback",
    ),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("stats/", views.CustomerStatsView.as_view(), name="stats"),
    path("account/", views.AccountView.as_view(), name="account"),
    path(
        "subscription/", views.SubscriptionView.as_view(), name="subscription"
    ),
    path(
        "subscription/create/",
        views.CustomerSubscriptionCreateView.as_view(),
        name="create subscription",
    ),
    path(
        "notifications/",
        views.NotificationsView.as_view(),
        name="notifications",
    ),
    path(
        "notifications/list/",
        views.WialonNotificationListView.as_view(),
        name="list notification",
    ),
    path(
        "notifications/create/",
        views.WialonNotificationCreateView.as_view(),
        name="create notification",
    ),
    path(
        "notifications/<int:notification_pk>/detail/",
        views.WialonNotificationDetailView.as_view(),
        name="detail notification",
    ),
    path(
        "notifications/<int:notification_pk>/update/",
        views.WialonNotificationUpdateView.as_view(),
        name="update notification",
    ),
    path(
        "notifications/<int:notification_pk>/delete/",
        views.WialonNotificationDeleteView.as_view(),
        name="delete notification",
    ),
]

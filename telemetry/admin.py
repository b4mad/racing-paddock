from django.contrib import admin
from django_admin_listfilter_dropdown.filters import DropdownFilter, RelatedDropdownFilter  # ChoiceDropdownFilter,
from django_admin_relation_links import AdminChangeLinksMixin

from .models import (
    Car,
    CarClass,
    Coach,
    Driver,
    FastLap,
    FastLapSegment,
    Game,
    Landmark,
    Lap,
    ReferenceSegment,
    Segment,
    Session,
    SessionType,
    SoundClip,
    Track,
    TrackGuide,
    TrackGuideNote,
)


class FastLapAdmin(AdminChangeLinksMixin, admin.ModelAdmin):
    list_display = ["track"]
    changelist_links = ["fast_lap_segments", "laps"]
    list_display = ["game", "car", "track", "driver", "created", "modified"]


class FastLapSegmentAdmin(AdminChangeLinksMixin, admin.ModelAdmin):
    list_display = [
        "fast_lap",
        "turn",
        "start",
        "end",
        "brake",
        "turn_in",
        "force",
        "gear",
        "stop",
        "accelerate",
        "speed",
        "mark",
    ]
    change_links = []


class LapAdmin(AdminChangeLinksMixin, admin.ModelAdmin):
    list_display = ["id", "get_driver", "valid", "completed", "number", "get_game", "track", "car", "time", "official_time"]
    list_display = [
        "id",
        "get_driver",
        "valid",
        "number",
        "get_game",
        "track",
        "car",
        "length",
        "time",
        "session",
        "start",
        "end",
    ]
    # list_filter = ["car", "track"]
    list_filter = (
        # for ordinary fields
        ("valid", DropdownFilter),
        # for choice fields
        # ('valid', ChoiceDropdownFilter),
        # for related fields
        ("car", RelatedDropdownFilter),
        ("track", RelatedDropdownFilter),
    )
    fields = ["number", "valid", "completed", "length", "time", "official_time", "start", "end", "session", "track", "car", "fast_lap"]
    changelist_links = ["session"]
    change_links = ["session", "track", "car"]

    # https://stackoverflow.com/questions/163823/can-list-display-in-a-django-modeladmin-display-attributes-of-foreignkey-field
    @admin.display(ordering="session__driver", description="Driver")
    def get_driver(self, obj):
        return obj.session.driver

    @admin.display(ordering="session__game", description="Game")
    def get_game(self, obj):
        return obj.session.game


class DriverAdmin(AdminChangeLinksMixin, admin.ModelAdmin):
    list_display = ["name", "created", "modified"]
    changelist_links = ["sessions"]


class SessionAdmin(AdminChangeLinksMixin, admin.ModelAdmin):
    list_display = ["session_id", "driver", "game", "track", "car", "session_type", "start"]
    fields = ["session_id", "driver", "game", "track", "car", "session_type", "start", "end"]
    changelist_links = ["laps"]


class TrackAdmin(AdminChangeLinksMixin, admin.ModelAdmin):
    list_display = ["name", "game", "length", "created", "modified"]
    changelist_links = ["laps", "landmarks", "fast_laps"]


class CarAdmin(AdminChangeLinksMixin, admin.ModelAdmin):
    list_display = ["name", "game", "car_class"]
    changelist_links = ["laps", "fast_laps"]


class CarClassAdmin(AdminChangeLinksMixin, admin.ModelAdmin):
    list_display = ["name", "game"]


class GameAdmin(AdminChangeLinksMixin, admin.ModelAdmin):
    list_display = ["name"]
    changelist_links = ["tracks", "cars", "sessions"]


class CoachAdmin(AdminChangeLinksMixin, admin.ModelAdmin):
    list_display = ["driver", "mode", "enabled", "status", "created", "modified"]
    fields = ["driver", "error", "status", "mode", "enabled", "fast_lap"]


class LandmarkAdmin(AdminChangeLinksMixin, admin.ModelAdmin):
    list_display = ["name", "kind", "track", "start", "end"]
    fields = ["name", "kind", "track", "start", "end", "is_overtaking_spot", "from_cc"]


class TrackGuideAdmin(AdminChangeLinksMixin, admin.ModelAdmin):
    list_display = ["car_game", "car", "track", "name", "created", "modified"]
    changelist_links = ["notes"]


class TrackGuideNoteAdmin(AdminChangeLinksMixin, admin.ModelAdmin):
    list_display = ["track_guide", "segment", "priority", "message"]
    fields = ["track_guide", "landmark", "segment", "finish_at", "at", "priority", "ref_id", "ref_eval", "sort_key", "mode", "message", "eval", "notes", "score"]


class SegmentAdmin(AdminChangeLinksMixin, admin.ModelAdmin):
    list_display = ["lap", "landmark", "kind", "braking_point", "apex", "gear"]
    fields = [
        "lap",
        "landmark",
        "kind",
        "braking_point",
        "lift_off_point",
        "acceleration_point",
        "brake_pressure",
        "brake_application_rate",
        "brake_release_rate",
        "throttle_lift",
        "throttle_application_rate",
        "throttle_release_rate",
        "apex",
        "entry_speed",
        "corner_speed",
        "exit_speed",
        "gear",
        "coasting_time",
        "launch_wheel_slip_time",
    ]


class ReferenceSegmentAdmin(AdminChangeLinksMixin, admin.ModelAdmin):
    list_display = ["lap", "landmark", "driver", "track"]


admin.site.register(Car, CarAdmin)
admin.site.register(CarClass, CarClassAdmin)
admin.site.register(SessionType)
admin.site.register(Lap, LapAdmin)
admin.site.register(Track, TrackAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(Driver, DriverAdmin)
admin.site.register(Session, SessionAdmin)
admin.site.register(FastLap, FastLapAdmin)
admin.site.register(FastLapSegment, FastLapSegmentAdmin)
admin.site.register(Coach, CoachAdmin)
admin.site.register(Landmark, LandmarkAdmin)
admin.site.register(TrackGuide, TrackGuideAdmin)
admin.site.register(TrackGuideNote, TrackGuideNoteAdmin)
admin.site.register(Segment, SegmentAdmin)
admin.site.register(ReferenceSegment, ReferenceSegmentAdmin)
admin.site.register(SoundClip)

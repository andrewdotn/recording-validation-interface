# Copyright (C) 2018 Eddie Antonio Santos <easantos@ualberta.ca>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Phrase, Recording, RecordingSession, Speaker, Issue

admin.site.register(Phrase, SimpleHistoryAdmin)
admin.site.register(RecordingSession)
admin.site.register(Speaker)  # TODO: use simplehistory
admin.site.register(Recording, SimpleHistoryAdmin)


class IssueAdmin(admin.ModelAdmin):
    readonly_fields = ("phrase", "recording")


admin.site.register(Issue, IssueAdmin)

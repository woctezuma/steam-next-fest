import datetime
import time

from download_ISteamApps import update_cache_of_store_data
from find_missing_demos_in_ISteamApps import fill_in_event_files_using_ISteamApps
from list_all_known_ids import compute_known_ids
from list_relevant_unowned_apps import keep_track_of_other_relevant_unowned_apps
from list_unowned_demos import keep_track_of_unowned_demos
from run_ajax_queries import perform_incremental_update_of_event_files


class TimeScheduler:
    def __init__(self, cooldown_in_sec, verbose=True):
        self.cooldown_in_sec = cooldown_in_sec
        self.verbose = verbose
        self._last_updated = None
        self._name = None

    def _get_delay(self):
        if self._last_updated is None:
            delay = None
        else:
            delay = time.time() - self._last_updated
        return delay

    def _print(self, message):
        if self.verbose:
            print(f"[{datetime.datetime.now()}] {message}")
        return

    def _get_start_message(self):
        return f"Querying {self._name} endpoint 👀"

    def _get_end_message(self):
        return f"Done with {self._name} 👌"

    def update(self):
        delay = self._get_delay()
        has_performed_update = bool(delay is None or delay > self.cooldown_in_sec)
        if has_performed_update:
            self._print(self._get_start_message())
            output = self._perform_update()
            self._print(self._get_end_message())
            self._last_updated = time.time()
        else:
            output = []
        return output, has_performed_update

    def _perform_update(self):
        raise NotImplemented


class AjaxScheduler(TimeScheduler):
    def __init__(self, cooldown_in_sec=45, verbose=True):
        super().__init__(cooldown_in_sec, verbose=verbose)
        self._name = "AJAX"

    def _perform_update(self):
        new_demo_ids = perform_incremental_update_of_event_files()
        return new_demo_ids


class SteamScheduler(TimeScheduler):
    def __init__(self, cooldown_in_sec=2700, verbose=True):
        super().__init__(cooldown_in_sec, verbose=verbose)
        self._name = "ISteamApps"

    def _perform_update(self):
        app_store_data = update_cache_of_store_data(verbose=self.verbose)
        new_demo_ids = fill_in_event_files_using_ISteamApps(verbose=self.verbose)
        return new_demo_ids


def update_cache_of_ids_to_monitor():
    unowned_demos = keep_track_of_unowned_demos()
    relevant_ids = keep_track_of_other_relevant_unowned_apps()
    known_ids = compute_known_ids(save_to_disk=True)
    return set(unowned_demos), set(relevant_ids), set(known_ids)

#include <pebble.h>

#define MAX_ITEMS 15
#define TITLE_LEN 64

static Window *s_window;
static MenuLayer *s_menu_layer;
static int s_item_count = 0;
static char s_titles[MAX_ITEMS][TITLE_LEN];

static void request_refresh(void) {
  DictionaryIterator *iter;
  if (app_message_outbox_begin(&iter) != APP_MSG_OK || !iter) return;
  dict_write_uint8(iter, MESSAGE_KEY_REQUEST_REFRESH, 1);
  app_message_outbox_send();
}

static void select_index(int index) {
  DictionaryIterator *iter;
  if (app_message_outbox_begin(&iter) != APP_MSG_OK || !iter) return;
  dict_write_int32(iter, MESSAGE_KEY_SELECT_INDEX, index);
  app_message_outbox_send();
}

static uint16_t menu_get_num_rows_callback(MenuLayer *menu_layer, uint16_t section_index, void *context) {
  return s_item_count > 0 ? s_item_count : 1;
}

static void menu_draw_row_callback(GContext *ctx, const Layer *cell_layer, MenuIndex *cell_index, void *context) {
  if (s_item_count == 0) {
    menu_cell_basic_draw(ctx, cell_layer, "Loading…", "Fetching daily digest", NULL);
    return;
  }
  menu_cell_basic_draw(ctx, cell_layer, s_titles[cell_index->row], NULL, NULL);
}

static void menu_select_callback(MenuLayer *menu_layer, MenuIndex *cell_index, void *context) {
  if (s_item_count == 0) return;
  select_index(cell_index->row);
}

static void inbox_received_callback(DictionaryIterator *iterator, void *context) {
  Tuple *count_t = dict_find(iterator, MESSAGE_KEY_ITEM_COUNT);
  if (count_t) {
    s_item_count = count_t->value->int32;
    if (s_item_count < 0) s_item_count = 0;
    if (s_item_count > MAX_ITEMS) s_item_count = MAX_ITEMS;
  }

  for (int i = 0; i < MAX_ITEMS; i++) {
    Tuple *t = dict_find(iterator, MESSAGE_KEY_ITEM_0 + i);
    if (t && t->type == TUPLE_CSTRING) {
      snprintf(s_titles[i], TITLE_LEN, "%s", t->value->cstring);
    }
  }

  layer_mark_dirty(menu_layer_get_layer(s_menu_layer));
}

static void inbox_dropped_callback(AppMessageResult reason, void *context) {
  APP_LOG(APP_LOG_LEVEL_WARNING, "Inbox dropped: %d", reason);
}

static void outbox_failed_callback(DictionaryIterator *iterator, AppMessageResult reason, void *context) {
  APP_LOG(APP_LOG_LEVEL_WARNING, "Outbox failed: %d", reason);
}

static void window_load(Window *window) {
  Layer *window_layer = window_get_root_layer(window);
  GRect bounds = layer_get_bounds(window_layer);

  s_menu_layer = menu_layer_create(bounds);
  menu_layer_set_callbacks(s_menu_layer, NULL, (MenuLayerCallbacks) {
    .get_num_rows = menu_get_num_rows_callback,
    .draw_row = menu_draw_row_callback,
    .select_click = menu_select_callback,
  });
  menu_layer_set_click_config_onto_window(s_menu_layer, window);
  layer_add_child(window_layer, menu_layer_get_layer(s_menu_layer));
}

static void window_unload(Window *window) {
  menu_layer_destroy(s_menu_layer);
}

static void init(void) {
  s_window = window_create();
  window_set_window_handlers(s_window, (WindowHandlers) {
    .load = window_load,
    .unload = window_unload,
  });

  window_stack_push(s_window, true);

  app_message_register_inbox_received(inbox_received_callback);
  app_message_register_inbox_dropped(inbox_dropped_callback);
  app_message_register_outbox_failed(outbox_failed_callback);
  app_message_open(4096, 512);

  request_refresh();
}

static void deinit(void) {
  window_destroy(s_window);
}

int main(void) {
  init();
  app_event_loop();
  deinit();
}

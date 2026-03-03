#include <pebble.h>

#define MAX_ITEMS 15
#define TITLE_LEN 96
#define DETAIL_LEN 1200

static Window *s_list_window, *s_detail_window;
static MenuLayer *s_menu_layer;
static ScrollLayer *s_detail_scroll;
static TextLayer *s_detail_title_layer, *s_detail_text_layer;

static int s_item_count = 0;
static char s_titles[MAX_ITEMS][TITLE_LEN];
static char s_detail_title[128];
static char s_detail_text[DETAIL_LEN];

static void request_refresh(void) {
  DictionaryIterator *iter;
  if (app_message_outbox_begin(&iter) != APP_MSG_OK || !iter) return;
  dict_write_uint8(iter, MESSAGE_KEY_REQUEST_REFRESH, 1);
  app_message_outbox_send();
}

static void request_detail(int index) {
  DictionaryIterator *iter;
  if (app_message_outbox_begin(&iter) != APP_MSG_OK || !iter) return;
  dict_write_int32(iter, MESSAGE_KEY_SELECT_INDEX, index);
  app_message_outbox_send();
}

static uint16_t menu_get_num_rows_callback(MenuLayer *menu_layer, uint16_t section_index, void *context) {
  return s_item_count > 0 ? s_item_count : 1;
}

static int16_t menu_get_cell_height_callback(MenuLayer *menu_layer, MenuIndex *cell_index, void *context) {
  return 44;
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
  snprintf(s_detail_title, sizeof(s_detail_title), "%s", s_titles[cell_index->row]);
  snprintf(s_detail_text, sizeof(s_detail_text), "Loading full text…");
  text_layer_set_text(s_detail_title_layer, s_detail_title);
  text_layer_set_text(s_detail_text_layer, s_detail_text);
  window_stack_push(s_detail_window, true);
  request_detail(cell_index->row);
}

static void detail_scroll_click_handler(ClickRecognizerRef recognizer, void *context) {
  int dir = (int)(intptr_t)context;
  GPoint offset = scroll_layer_get_content_offset(s_detail_scroll);
  int step = 36; // ~two lines per click
  offset.y += dir * step;
  if (offset.y > 0) offset.y = 0;

  GRect bounds = layer_get_bounds(window_get_root_layer(s_detail_window));
  GSize content = scroll_layer_get_content_size(s_detail_scroll);
  int min_y = bounds.size.h - content.h;
  if (min_y > 0) min_y = 0;
  if (offset.y < min_y) offset.y = min_y;

  scroll_layer_set_content_offset(s_detail_scroll, offset, true);
}

static void detail_click_config_provider(void *context) {
  window_single_click_subscribe(BUTTON_ID_UP, detail_scroll_click_handler);
  window_single_click_subscribe(BUTTON_ID_DOWN, detail_scroll_click_handler);
  window_set_click_context(BUTTON_ID_UP, (void *)(intptr_t)1);
  window_set_click_context(BUTTON_ID_DOWN, (void *)(intptr_t)-1);
}

static void update_detail_layout(void) {
  GRect bounds = layer_get_bounds(window_get_root_layer(s_detail_window));
  int y = 4;
  text_layer_set_text(s_detail_title_layer, s_detail_title);
  text_layer_set_text(s_detail_text_layer, s_detail_text);

  GSize title_size = text_layer_get_content_size(s_detail_title_layer);
  layer_set_frame(text_layer_get_layer(s_detail_title_layer), GRect(4, y, bounds.size.w - 8, title_size.h + 4));
  y += title_size.h + 8;

  layer_set_frame(text_layer_get_layer(s_detail_text_layer), GRect(4, y, bounds.size.w - 8, 2000));
  GSize text_size = text_layer_get_content_size(s_detail_text_layer);
  layer_set_frame(text_layer_get_layer(s_detail_text_layer), GRect(4, y, bounds.size.w - 8, text_size.h + 8));

  int content_h = y + text_size.h + 16;
  scroll_layer_set_content_size(s_detail_scroll, GSize(bounds.size.w, content_h));
}

static void inbox_received_callback(DictionaryIterator *iterator, void *context) {
  Tuple *count_t = dict_find(iterator, MESSAGE_KEY_ITEM_COUNT);
  Tuple *start_t = dict_find(iterator, MESSAGE_KEY_BATCH_START);

  if (count_t) {
    s_item_count = count_t->value->int32;
    if (s_item_count < 0) s_item_count = 0;
    if (s_item_count > MAX_ITEMS) s_item_count = MAX_ITEMS;
  }

  int start = start_t ? start_t->value->int32 : 0;
  for (int i = 0; i < MAX_ITEMS; i++) {
    Tuple *t = dict_find(iterator, MESSAGE_KEY_ITEM_0 + i);
    if (t && t->type == TUPLE_CSTRING) {
      int idx = start + i;
      if (idx >= 0 && idx < MAX_ITEMS) {
        snprintf(s_titles[idx], TITLE_LEN, "%s", t->value->cstring);
      }
    }
  }

  Tuple *dt = dict_find(iterator, MESSAGE_KEY_DETAIL_TITLE);
  Tuple *dx = dict_find(iterator, MESSAGE_KEY_DETAIL_TEXT);
  if (dt && dt->type == TUPLE_CSTRING) {
    snprintf(s_detail_title, sizeof(s_detail_title), "%s", dt->value->cstring);
  }
  if (dx && dx->type == TUPLE_CSTRING) {
    snprintf(s_detail_text, sizeof(s_detail_text), "%s", dx->value->cstring);
  }
  if (dt || dx) {
    update_detail_layout();
  }

  layer_mark_dirty(menu_layer_get_layer(s_menu_layer));
}

static void window_list_load(Window *window) {
  Layer *window_layer = window_get_root_layer(window);
  GRect bounds = layer_get_bounds(window_layer);

  s_menu_layer = menu_layer_create(bounds);
  menu_layer_set_callbacks(s_menu_layer, NULL, (MenuLayerCallbacks) {
    .get_num_rows = menu_get_num_rows_callback,
    .get_cell_height = menu_get_cell_height_callback,
    .draw_row = menu_draw_row_callback,
    .select_click = menu_select_callback,
  });
  menu_layer_set_click_config_onto_window(s_menu_layer, window);
  layer_add_child(window_layer, menu_layer_get_layer(s_menu_layer));
}

static void window_list_unload(Window *window) {
  menu_layer_destroy(s_menu_layer);
}

static void window_detail_load(Window *window) {
  Layer *root = window_get_root_layer(window);
  GRect bounds = layer_get_bounds(root);

  s_detail_scroll = scroll_layer_create(bounds);
  scroll_layer_set_click_config_onto_window(s_detail_scroll, window);
  window_set_click_config_provider(window, detail_click_config_provider);

  s_detail_title_layer = text_layer_create(GRect(4, 4, bounds.size.w - 8, 40));
  text_layer_set_font(s_detail_title_layer, fonts_get_system_font(FONT_KEY_GOTHIC_24_BOLD));
  text_layer_set_text(s_detail_title_layer, "");
  text_layer_set_text_alignment(s_detail_title_layer, GTextAlignmentLeft);

  s_detail_text_layer = text_layer_create(GRect(4, 48, bounds.size.w - 8, 400));
  text_layer_set_font(s_detail_text_layer, fonts_get_system_font(FONT_KEY_GOTHIC_24));
  text_layer_set_text(s_detail_text_layer, "");
  text_layer_set_text_alignment(s_detail_text_layer, GTextAlignmentLeft);

  scroll_layer_add_child(s_detail_scroll, text_layer_get_layer(s_detail_title_layer));
  scroll_layer_add_child(s_detail_scroll, text_layer_get_layer(s_detail_text_layer));
  layer_add_child(root, scroll_layer_get_layer(s_detail_scroll));
}

static void window_detail_unload(Window *window) {
  text_layer_destroy(s_detail_title_layer);
  text_layer_destroy(s_detail_text_layer);
  scroll_layer_destroy(s_detail_scroll);
}

static void init(void) {
  s_list_window = window_create();
  window_set_window_handlers(s_list_window, (WindowHandlers){
    .load = window_list_load,
    .unload = window_list_unload,
  });

  s_detail_window = window_create();
  window_set_window_handlers(s_detail_window, (WindowHandlers){
    .load = window_detail_load,
    .unload = window_detail_unload,
  });

  window_stack_push(s_list_window, true);

  app_message_register_inbox_received(inbox_received_callback);
  app_message_open(4096, 512);

  request_refresh();
}

static void deinit(void) {
  window_destroy(s_detail_window);
  window_destroy(s_list_window);
}

int main(void) {
  init();
  app_event_loop();
  deinit();
}

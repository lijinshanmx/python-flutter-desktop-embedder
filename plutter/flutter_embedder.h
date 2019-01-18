typedef struct _FlutterEngine* FlutterEngine;
typedef enum {
  kSuccess = 0,
  kInvalidLibraryVersion,
  kInvalidArguments,
} FlutterResult;
typedef enum {
  kOpenGL,
} FlutterRendererType;
typedef bool (*BoolCallback)(void* );
typedef bool (*FPlatfromMessageCallback)(void* );
typedef uint32_t (*UIntCallback)(void* );
typedef struct {
  size_t struct_size;
  BoolCallback make_current;
  BoolCallback clear_current;
  BoolCallback present;
  UIntCallback fbo_callback;
  BoolCallback make_resource_current;
} FlutterOpenGLRendererConfig;
typedef struct {
  FlutterEngine engine;
  double monitor_screen_coordinates_per_inch;
  double window_pixels_per_screen_coordinate;
} FlutterEmbedderState;
typedef struct {
  FlutterRendererType type;
  union {
    FlutterOpenGLRendererConfig open_gl;
  };
} FlutterRendererConfig;
typedef struct {
  size_t struct_size;
  size_t width;
  size_t height;
  double pixel_ratio;
} FlutterWindowMetricsEvent;
typedef enum {
  kCancel,
  kUp,
  kDown,
  kMove,
} FlutterPointerPhase;
typedef struct {
  size_t struct_size;
  FlutterPointerPhase phase;
  size_t timestamp;  // in microseconds.
  double x;
  double y;
} FlutterPointerEvent;
struct _FlutterPlatformMessageResponseHandle;
typedef struct _FlutterPlatformMessageResponseHandle
    FlutterPlatformMessageResponseHandle;
typedef struct {
  size_t struct_size;
  const char* channel;
  const uint8_t* message;
  const size_t message_size;
  const FlutterPlatformMessageResponseHandle* response_handle;
} FlutterPlatformMessage;
typedef void (*FlutterPlatformMessageCallback)(
    const FlutterPlatformMessage*,
    void* );
typedef struct {
  size_t struct_size;
  const char* assets_path;
  const char* main_path;
  const char* packages_path;
  const char* icu_data_path;
  int command_line_argc;
  const char* const* command_line_argv;
  FlutterPlatformMessageCallback platform_message_callback;
} FlutterProjectArgs;
FlutterResult FlutterEngineRun(size_t version,
                               const FlutterRendererConfig* config,
                               const FlutterProjectArgs* args,
                               void* user_data,
                               FlutterEngine* engine_out);
FlutterResult FlutterEngineShutdown(FlutterEngine engine);
FlutterResult FlutterEngineSendWindowMetricsEvent(
    FlutterEngine engine,
    const FlutterWindowMetricsEvent* event);
FlutterResult FlutterEngineSendPointerEvent(FlutterEngine engine,
                                            const FlutterPointerEvent* events,
                                            size_t events_count);
FlutterResult FlutterEngineSendPlatformMessage(
    FlutterEngine engine,
    const FlutterPlatformMessage* message);
FlutterResult FlutterEngineSendPlatformMessageResponse(
    FlutterEngine engine,
    const FlutterPlatformMessageResponseHandle* handle,
    const uint8_t* data,
    size_t data_length);
FlutterResult __FlutterEngineFlushPendingTasksNow();
typedef struct {
  FlutterEngine engine;
  BoolCallback FMakeCurrent;
  BoolCallback FClearCurrent;
  BoolCallback FPresent;
  UIntCallback FFboCallback;
  BoolCallback FMakeResourceCurrent;
} EngineOpenGL;
typedef struct {
  float clientID;
  int* word;
  int selectionBase;
  int selectionExtent;
} textModel;
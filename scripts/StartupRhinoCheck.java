import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

/** 설치된 Rhino를 직접 읽어 번역 스크립트의 초기화와 콜백을 검사해요. */
public class StartupRhinoCheck {
    public static class RealComponent {
        private final String text;
        public RealComponent(String text) { this.text = text; }
        public static RealComponent literal(String text) { return new RealComponent(text); }
        public String getString() { return text; }
    }
    public static class RealWidget {
        public String text;
        public RealWidget(String text) { this.text = text; }
        public RealComponent getMessage() { return new RealComponent(text); }
        public void setMessage(RealComponent text) { this.text = text.getString(); }
    }
    public static class RealScreen {
        private final List<Object> widgets = new ArrayList<>();
        public List<Object> children() { return widgets; }
        public void addWidget(Object widget) { widgets.add(widget); }
    }
    public static class RealConfigScreen extends RealScreen {}
    public static class RealScreenEvent {
        private final RealScreen screen;
        public RealScreenEvent(RealScreen screen) { this.screen = screen; }
        public RealScreen getScreen() { return screen; }
        public List<Object> getListenersList() { return screen.children(); }
    }

    public static void main(String[] args) throws Exception {
        Class<?> factory = Class.forName("dev.latvian.mods.rhino.ContextFactory");
        Object context = factory.getMethod("enter").invoke(factory.getConstructor().newInstance());
        Class<?> contextClass = context.getClass();
        Method evaluate = contextClass.getMethod("evaluateString",
            Class.forName("dev.latvian.mods.rhino.Scriptable"),
            String.class, String.class, int.class, Object.class);
        Object scope = contextClass.getMethod("initStandardObjects").invoke(context);
        Class<?> scriptable = Class.forName("dev.latvian.mods.rhino.Scriptable");
        Method wrap = contextClass.getMethod("wrapJavaClass", scriptable, Class.class);
        Method put = Class.forName("dev.latvian.mods.rhino.ScriptableObject").getMethod(
            "putProperty", scriptable, String.class, Object.class, contextClass);
        for (Class<?> type : new Class<?>[] {RealComponent.class, RealWidget.class,
            RealScreen.class, RealConfigScreen.class, RealScreenEvent.class}) {
            put.invoke(null, scope, type.getSimpleName(), wrap.invoke(context, scope, type), context);
        }
        try {
            for (String file : args) {
                evaluate.invoke(context, scope, Files.readString(Path.of(file)), file, 1, null);
            }
        } catch (InvocationTargetException exception) {
            throw new RuntimeException("Rhino 실행 검사 실패", exception.getCause());
        }
        System.out.println("Rhino 실행 검사 통과");
    }
}

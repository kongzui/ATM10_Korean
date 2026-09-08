import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.nio.file.Files;
import java.nio.file.Path;

/** 설치된 Rhino를 직접 읽어 번역 스크립트의 초기화와 콜백을 검사해요. */
public class StartupRhinoCheck {
    public static void main(String[] args) throws Exception {
        Class<?> factory = Class.forName("dev.latvian.mods.rhino.ContextFactory");
        Object context = factory.getMethod("enter").invoke(factory.getConstructor().newInstance());
        Class<?> contextClass = context.getClass();
        Method evaluate = contextClass.getMethod("evaluateString",
            Class.forName("dev.latvian.mods.rhino.Scriptable"),
            String.class, String.class, int.class, Object.class);
        Object scope = contextClass.getMethod("initStandardObjects").invoke(context);
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

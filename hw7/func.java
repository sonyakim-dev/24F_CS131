import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class Kotainer<T extends Comparable<T>> {
  private List<T> elements;
  private static final int MAX_SIZE = 100;

  public Kotainer() {
    elements = new ArrayList<>();
  }
  public void add(T element) {
    if (elements.size() < MAX_SIZE) {
      elements.add(element);
    }
  }
  public T getMin() {
    return Collections.min(elements);
  }
  public static void main(String[] args) {
    Kotainer<Double> kotainer_double = new Kotainer<>();
    kotainer_double.add(1.0);
    kotainer_double.add(2.0);
    kotainer_double.add(3.0);
    System.out.println(kotainer_double.getMin());

    Kontainer<String> kotainer_string = new Kotainer<>();
    kotainer_string.add("cat");
    kotainer_string.add("dog");
    kotainer_string.add("elephant");
    System.out.println(kotainer_string.getMin());
  }
}


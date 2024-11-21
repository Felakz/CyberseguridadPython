package Vista;
import Controlador.GestorAutores;
import Modelo.Publicacion;
import java.util.Scanner;

public class RegistroAutores {
    public static void main(String[] args) {
        GestorAutores gestor = new GestorAutores();
        Scanner scanner = new Scanner(System.in);
        int opcion;
        do {
            System.out.println("=== Menú de Gestión de Autores ===");
            System.out.println("1. Crear un nuevo autor");
            System.out.println("2. Mostrar lista de autores y publicaciones");
            System.out.println("3. Salir");
            System.out.print("Selecciona una opción: ");
            opcion = scanner.nextInt();
            scanner.nextLine(); // Limpiar el buffer
            switch (opcion) {
                case 1:
                    System.out.print("Nombre del autor: ");
                    String nombre = scanner.nextLine();
                    System.out.print("Filiación: ");
                    String filiacion = scanner.nextLine();
                    System.out.print("Línea de investigación: ");
                    String lineaInvestigacion = scanner.nextLine();
                    System.out.print("Nacionalidad: ");
                    String nacionalidad = scanner.nextLine();
                    System.out.print("Cantidad de publicaciones: ");
                    int cantidadPublicaciones = scanner.nextInt();
                    scanner.nextLine(); // Limpiar el buffer
                    Publicacion[] publicaciones = new Publicacion[cantidadPublicaciones];
                    for (int i = 0; i < cantidadPublicaciones; i++) {
                        System.out.println("Publicación " + (i + 1) + ":");
                        System.out.print("Año: ");
                        int anio = scanner.nextInt();
                        scanner.nextLine(); // Limpiar el buffer
                        System.out.print("Nombre de la revista: ");
                        String nombreRevista = scanner.nextLine();
                        System.out.print("Título: ");
                        String titulo = scanner.nextLine();
                        publicaciones[i] = new Publicacion(anio, nombreRevista, titulo);
                    }
                    gestor.crearAutor(filiacion, lineaInvestigacion, nacionalidad, nombre, publicaciones);
                    System.out.println("Autor creado exitosamente.\n");
                    break;
                case 2:System.out.println("Lista de Autores:");
                    gestor.imprimirAutores();
                    break;
                case 3:System.out.println("Saliendo del sistema...");
                    break;
                default:System.out.println("Opción no válida. Intenta nuevamente.\n");
            }
        } while (opcion != 3);
        scanner.close();
    }}



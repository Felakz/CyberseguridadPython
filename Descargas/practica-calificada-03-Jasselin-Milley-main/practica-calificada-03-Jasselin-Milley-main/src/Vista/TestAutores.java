package Vista;



import Controlador.GestorAutores;
import Modelo.Publicacion;


public class TestAutores {
    public static void main(String[] args) {
        System.out.println("=== Test: Verificar datos registrados desde RegistroAutores ===");

        GestorAutores gestor = new GestorAutores();
        RegistroAutores.main(null); 
        System.out.println("\n=== Autores registrados ===");
        
        gestor.imprimirAutores();
    }
}


package Controlador;

import Modelo.Autor;
import Modelo.Publicacion;

public class GestorAutores {
    private static final int CANTIDAD_MAXIMA_AUTORES = 10;
    private Autor[] autores;
    private int contadorAutores;

    public GestorAutores() {
        this.autores = new Autor[CANTIDAD_MAXIMA_AUTORES];
        this.contadorAutores = 0;
    }
    public void crearAutor(String filiacion, String lineaInvestigacion, String nacionalidad, String nombre, Publicacion[] publicaciones) {
        if (contadorAutores < CANTIDAD_MAXIMA_AUTORES) {
            Autor nuevoAutor = new Autor(filiacion, lineaInvestigacion, nacionalidad, nombre);
            for (Publicacion publicacion : publicaciones) {
                if (publicacion != null) {
                    nuevoAutor.agregarPublicacion(publicacion);
                }
            }
            autores[contadorAutores] = nuevoAutor;
            contadorAutores++;
        } else {
            System.out.println("No se puede agregar más autores. Límite alcanzado.");
        }
    }

    public void imprimirAutores() {
        if (contadorAutores == 0) {
            System.out.println("No hay autores registrados.");
            return;
        }

        for (int i = 0; i < contadorAutores; i++) {
            System.out.println(autores[i]);
        }
    }
}

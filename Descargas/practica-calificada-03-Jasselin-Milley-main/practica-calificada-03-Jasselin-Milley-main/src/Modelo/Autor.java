package Modelo;
public class Autor {    
    private static final int MAX_PUBLICACIONES = 5;
    private int cantidadPublicaciones;
    private String filiacion;
    private String lineaInvestigacion;
    private String nacionalidad;
    private String nombre;
    private Publicacion[] publicaciones;
    public Autor(String filiacion, String lineaInvestigacion, String nacionalidad, String nombre) {
        this.filiacion = filiacion;
        this.lineaInvestigacion = lineaInvestigacion;
        this.nacionalidad = nacionalidad;
        this.nombre = nombre;
        this.publicaciones = new Publicacion[MAX_PUBLICACIONES];
        this.cantidadPublicaciones = 0;
    }
    public void agregarPublicacion(Publicacion publicacionNueva) {
        if (cantidadPublicaciones < MAX_PUBLICACIONES) {
            publicaciones[cantidadPublicaciones] = publicacionNueva;
            cantidadPublicaciones++;
        } else {
            System.out.println("No se puede agregar más publicaciones. Límite alcanzado.");
        }}
    public int getCantidadPublicaciones() {return cantidadPublicaciones;}
    public String getFiliacion() {return filiacion;}
    public void setFiliacion(String filiacion) {this.filiacion = filiacion;    }
    public String getLineaInvestigacion() {return lineaInvestigacion;}
    public void setLineaInvestigacion(String lineaInvestigacion) {this.lineaInvestigacion = lineaInvestigacion;}
    public String getNacionalidad() {return nacionalidad;}
    public void setNacionalidad(String nacionalidad) {this.nacionalidad = nacionalidad;}
    public String getNombre() {return nombre;}
    public void setNombre(String nombre) {this.nombre = nombre;}
    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append("Autor{")
          .append("nombre='").append(nombre).append('\'')
          .append(", filiacion='").append(filiacion).append('\'')
          .append(", lineaInvestigacion='").append(lineaInvestigacion).append('\'')
          .append(", nacionalidad='").append(nacionalidad).append('\'')
          .append(", publicaciones=[");

        for (int i = 0; i < cantidadPublicaciones; i++) {
            sb.append(publicaciones[i].toString());
            if (i < cantidadPublicaciones - 1) {
                sb.append(", ");
            }
        }
        sb.append("]}");
        return sb.toString();
    }}

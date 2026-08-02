// ============ Mostrar / Ocultar modales (igual que antes) ============

function mostrarVentana(elementId) {
   document.getElementById(elementId).style.display = "flex";
}

function ocultarVentana(elementId) {
   document.getElementById(elementId).style.display = "none";
}

// ============ Helpers de formato ============

function pad(numero) {
   return String(numero).padStart(2, "0");
}

function etiquetaDia(dia, mes, anio, tipo) {
   if (tipo === "today") return "HOY";
   if (tipo === "tomorrow") return "MAÑANA";
   return `EL ${dia}/${mes}/${anio}`;
}

// ============ Tarjetas de #EVENTS (resumen semanal) ============

function crearTarjetaRecordatorio(recordatorio, tipo) {
   // recordatorio = [nombre, year, month, day, hour, minute]
   const [nombre, anio, mes, dia, hora, minuto] = recordatorio;

   const card = document.createElement("div");
   card.className = "EVENTCARD";

   const titulo = document.createElement("h6");
   titulo.className = "EVENTCARDTITLE";
   titulo.textContent = nombre;

   const detalle = document.createElement("span");
   detalle.className = "EVENTCARDDETAIL";
   detalle.textContent = `${etiquetaDia(dia, mes, anio, tipo)} a las ${hora}:${pad(minuto)}`;

   card.appendChild(titulo);
   card.appendChild(detalle);
   return card;
}

function pintarEventosSemana() {
   const contenedor = document.getElementById("EVENTS");
   if (!contenedor) return;

   contenedor.innerHTML = ""; // limpiar antes de pintar, evita duplicados

   TODAY_REMINDERS.forEach(r => contenedor.appendChild(crearTarjetaRecordatorio(r, "today")));
   TOMORROW_REMINDERS.forEach(r => contenedor.appendChild(crearTarjetaRecordatorio(r, "tomorrow")));
   OTHER_REMINDERS.forEach(r => contenedor.appendChild(crearTarjetaRecordatorio(r, "other")));
}

// ============ Listas dentro de los modales (ver / editar / borrar) ============
// Reemplaza a cargarEventosSee / cargarEventosDelete / cargarEventosEdit,
// que antes eran tres funciones casi idénticas copiadas y pegadas.

function crearFilaEvento(index, modo) {
   const { names, years, months, days, hours, minutes } = ALL_REMINDERS;

   const fila = document.createElement("div");
   fila.className = "EVENTROW";

   const info = document.createElement("div");
   info.className = "EVENTROWINFO";

   const titulo = document.createElement("h3");
   titulo.textContent = names[index];

   const detalle = document.createElement("span");
   detalle.className = "EVENTROWDETAIL";
   detalle.textContent =
      `PROGRAMADO PARA EL ${days[index]}/${months[index]}/${years[index]} A LAS ${hours[index]}:${pad(minutes[index])}`;

   info.appendChild(titulo);
   info.appendChild(detalle);
   fila.appendChild(info);

   // Guardamos el dato crudo en el propio elemento — nada de volver
   // a leer y parsear el texto que acabamos de escribir.
   fila.dataset.nombre = names[index];
   fila.dataset.anio = years[index];
   fila.dataset.mes = months[index];
   fila.dataset.dia = days[index];
   fila.dataset.hora = hours[index];
   fila.dataset.minuto = minutes[index];

   if (modo === "delete") {
      const boton = document.createElement("button");
      boton.className = "REMOVEBUTTON";
      boton.type = "button";
      boton.textContent = "ELIMINAR";
      boton.addEventListener("click", () => eliminarRecordatorio(fila.dataset));
      fila.appendChild(boton);
   }

   if (modo === "edit") {
      const boton = document.createElement("button");
      boton.className = "EDITBUTTONSMALL";
      boton.type = "button";
      boton.textContent = "EDITAR";
      boton.addEventListener("click", () => abrirFormularioEdicion(fila.dataset));
      fila.appendChild(boton);
   }

   return fila;
}

function pintarListaEventos(containerId, modo) {
   const contenedor = document.getElementById(containerId);
   contenedor.innerHTML = ""; // clave: limpiar antes de repintar

   for (let i = 0; i < ALL_REMINDERS.names.length; i++) {
      contenedor.appendChild(crearFilaEvento(i, modo));
   }
}

function eliminarRecordatorio(datos) {
   const params = new URLSearchParams({
      yearSTR: datos.anio,
      monthSTR: datos.mes,
      daySTR: datos.dia,
      hourSTR: datos.hora,
      minuteSTR: datos.minuto,
      remindSTR: datos.nombre,
   });
   window.location.href = "/remindRemove?" + params.toString();
}

function abrirFormularioEdicion(datos) {
   ocultarVentana("EDITEVENTSWINDOW");
   mostrarVentana("EDITREMINDWINDOW");

   const diaConCero = String(datos.dia).padStart(2, "0");
   const mesConCero = String(datos.mes).padStart(2, "0");

   document.getElementById("fechaEdit").value = `${datos.anio}-${mesConCero}-${diaConCero}`;
   document.getElementById("horaEdit").value = `${String(datos.hora).padStart(2, "0")}:${pad(datos.minuto)}`;
   document.getElementById("nameRemindEdit").value = datos.nombre;

   document.getElementById("yearSTR").value = datos.anio;
   document.getElementById("monthSTR").value = datos.mes;
   document.getElementById("daySTR").value = diaConCero;
   document.getElementById("hourSTR").value = datos.hora;
   document.getElementById("minuteSTR").value = datos.minuto;
   document.getElementById("remindSTR").value = datos.nombre;
}

// ============ Enganchar todo al abrir cada modal ============
// En vez de pintar la lista "a mano" desde un <script> suelto dentro del
// HTML (como estaba antes), la pintamos justo cuando el modal se abre.

document.addEventListener("DOMContentLoaded", () => {
   pintarEventosSemana();

   document.getElementById("SEEALLBUTTON")
      .addEventListener("click", () => pintarListaEventos("SEEEVENTSLIST", "see"));

   document.getElementById("DELETEBUTTON")
      .addEventListener("click", () => pintarListaEventos("DELETEEVENTSLIST", "delete"));

   document.getElementById("EDITBUTTON")
      .addEventListener("click", () => pintarListaEventos("EDITEVENTSLIST", "edit"));
});
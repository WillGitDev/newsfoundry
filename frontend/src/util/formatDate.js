import { getISOWeek, format } from "date-fns";
import { fr } from "date-fns/locale";

/***
 * Retourne la date au format 00/00/00
 */
export function formatDate(date) {
  return new Date(date).toLocaleDateString("fr-FR");
}

/**
 * Retourne le numéro de la semaine
 */
export function getWeeksNumber(date) {
  return getISOWeek(new Date(date));
}

/**
 * Retourne la date sous le format : lundi 1 janvier 2000 à 00:00
 * @param {String} date
 */
export function formatDateLong(date) {
  return format(new Date(date), "EEEE d MMMM yyyy 'à' HH'h'mm", { locale: fr });
}

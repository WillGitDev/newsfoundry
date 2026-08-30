import styles from "./cardRevue.module.css";
import { getWeeksNumber, formatDateLong } from "@/util/formatDate";
import ReactMarkdown from "react-markdown";
import { toast } from "react-hot-toast";

export default function CardRevue({ title, date, synthese }) {
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(synthese);
      toast.success("Revue copiée dans le presse papier");
    } catch (err) {
      toast.error("Impossible de copier la revue");
    }
  };
  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h3 className={styles.h3}>
          ACTUALITÉS {title} - SEMAINE {getWeeksNumber(date)}
        </h3>
        <p className={styles.date}>{formatDateLong(date)}</p>
        <button type="button" className={styles.button} onClick={handleCopy}>
          Copier
        </button>
      </div>
      <div className={styles.content}>
        <ReactMarkdown>{synthese}</ReactMarkdown>
      </div>
    </div>
  );
}

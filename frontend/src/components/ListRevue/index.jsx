import { toast } from "react-hot-toast";
import Loader from "@components/Loader";
import { useFetch } from "@/hooks/useFetch";
import { useEffect } from "react";
import styles from "./listRevue.module.css";
import CardRevue from "@components/CardRevue";

export default function ListRevue() {
  const { data: revues, loading, error } = useFetch("/revues");

  useEffect(() => {
    if (error) {
      toast.error(error.message);
    }
  }, [error]);
  return (
    <div className={styles.container}>
      <div>
        <h1 className={styles.title}>Reves de Presse</h1>
        <h2 className={styles.h2}>
          Consultez et gérer vos revues de presse générées par l'IA
        </h2>
      </div>
      {loading && <Loader />}
      {revues?.map((revue) => (
        <CardRevue
          key={revue.id}
          title={revue.titre}
          date={revue.revue_generated_at}
          synthese={revue.synthese_generale}
        />
      ))}
    </div>
  );
}

import styles from "./infoChat.module.css";
import Image from "next/image";

export default function InfoChat() {
  return (
    <div className={styles.container}>
      <Image
        src="/logo_head_robot.svg"
        width={80}
        height={70}
        alt="Logo d'une tête de robot"
      />
      <h1 className={styles.title}>Assistant Revue de Presse IA</h1>
      <h2 className={styles.h2}>
        Posez-moi des questions sur l'actualité récente ou demandez-moi de
        générer une revue de presse sur un sujet spécifique
      </h2>
      <p className={styles.example}>Exemples :</p>
      <ul>
        <li className={styles.li}>
          "Quelles sont les dernières nouvelles en politique ?"
        </li>
        <li className={styles.li}>
          "Génère une revue de presse sur la technologie"
        </li>
        <li className={styles.li}>
          "Résume l'actualité économique de la semaine"
        </li>
      </ul>
    </div>
  );
}

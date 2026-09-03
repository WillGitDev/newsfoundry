import styles from "./loader.module.css";

export default function Loader() {
  return (
    <div className={styles.container} role="status">
      <div className={styles.spinner}></div>
      <span className={styles.srOnly}>Chargement en cours</span>
    </div>
  );
}

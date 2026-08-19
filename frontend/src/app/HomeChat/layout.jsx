import styles from "./layout.module.css";

export default function HomeChatLayout({ children }) {
  return <div className={styles.container}>{children}</div>;
}

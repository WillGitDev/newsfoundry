import styles from "./revues.module.css";
import Chat from "@components/Chat";
import PastChat from "@components/PastChat";
import NavChat from "@components/NavChat";

export default function Revues() {
  return (
    <div className={styles.container}>
      <PastChat />
      <div className={styles.chatContainer}>
        <NavChat />
        <Chat mode="revues" />
      </div>
    </div>
  );
}

import styles from "./chatMessageBubble.module.css";
import ReactMarkdown from "react-markdown";
import Image from "next/image";
import { formatTime } from "@/util/formatTime";

export default function ChatMessageBubble({ role, content, timestamp }) {
  const isUser = role == "user";
  return (
    <div className={isUser ? styles.userBubble : styles.assistantBubble}>
      <div
        className={`${styles.containerIcon} ${isUser ? styles.userIcon : styles.ia}`}
      >
        {isUser ? (
          <Image src="/icon_person.svg" height={20} width={16} alt="" />
        ) : (
          <Image src="/logo_head_robot.svg" height={20} width={16} alt="" />
        )}
      </div>
      <div className={styles.container}>
        <div className={styles.containerContent}>
          <ReactMarkdown>{content}</ReactMarkdown>
          <p className={styles.time}>{formatTime(timestamp)}</p>
        </div>
      </div>
    </div>
  );
}

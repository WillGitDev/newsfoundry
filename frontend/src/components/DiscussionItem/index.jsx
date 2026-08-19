import styles from "./discussionItem.module.css";
import Link from "next/link";
import { formatDate } from "@/util/formatDate";

export default function DiscussionItem({ id, date }) {
  return (
    <Link href={`/HomeChat/${id}`} className={styles.container}>
      <p className={styles.content}>Discussion du</p>
      <p className={styles.date}>{formatDate(date)}</p>
    </Link>
  );
}

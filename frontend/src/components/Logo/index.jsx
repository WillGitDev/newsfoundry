import styles from "./logo.module.css";
import Image from "next/image";

export default function Logo() {
  return (
    <div className={styles.container}>
      <p className={styles.title}>NEWSFOUNDRY</p>
      <Image
        src="/logo_head_robot.svg"
        height={20}
        width={16}
        alt="logo de NewsFoundry une tête de robot"
      />
    </div>
  );
}

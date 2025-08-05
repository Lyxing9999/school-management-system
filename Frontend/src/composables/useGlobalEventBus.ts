import mitt from "mitt";

type Events = {
  "error-message": string;
  "session-expired": void;
};

export const eventBus = mitt<Events>();

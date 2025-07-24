export enum Day {
  Monday = "Monday",
  Tuesday = "Tuesday",
  Wednesday = "Wednesday",
  Thursday = "Thursday",
  Friday = "Friday",
  Saturday = "Saturday",
  Sunday = "Sunday",
}

export enum Shift {
  Morning = "M",
  Afternoon = "A",
  Evening = "E",
}

export interface ScheduleItem {
  _id?: string;
  
  day: Day;
  shift: Shift;
  start_time: string; // Format: HH:MM
  end_time: string; // Format: HH:MM
  room: string;
}


import type { ScheduleItem } from "~/types/models/Schedule";
import { Day, Shift } from "~/types/models/Schedule";
import { ObjectId } from "bson"; 

export class ScheduleItemModel implements ScheduleItem {
  _id?: string;
  day: Day;
  shift: Shift;
  start_time: string; // Format: "HH:MM"
  end_time: string;   // Format: "HH:MM"
  room: string;

  constructor(data: Partial<ScheduleItem> = {}) {
    this._id = data._id ?? new ObjectId().toString(); // Use crypto or UUID if you don't use BSON
    this.day = data.day ?? Day.Monday;
    this.shift = data.shift ?? Shift.Morning;
    this.start_time = data.start_time ?? "00:00";
    this.end_time = data.end_time ?? "00:00";
    this.room = data.room?.trim() ?? "";
  }

  toDict(): Record<string, any> {
    return {
      _id: this._id,
      day: this.day,
      shift: this.shift,
      start_time: this.start_time,
      end_time: this.end_time,
      room: this.room,
    };
  }
}
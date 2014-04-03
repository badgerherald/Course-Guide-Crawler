import sqlite3


class SqlitePipeline(object):
    def __init__(self):
        self.conn = sqlite3.connect("classes.db")
        c = self.conn.cursor()
        c.execute("""create table if not exists courses
                  (department text,
                  course_num text,
                  course_title text,
                  credits text,
                  desc text,
                  last_taught text,
                  description text,
                  pReq text)""")
        c.execute("""create table if not exists sections
                  (department text,
                  course_num text,
                  course_title text,
                  last_updated text,
                  class_no text,
                  sec_no text,
                  session text,
                  time text,
                  place text,
                  teacher text,
                  credits text,
                  openSeats text,
                  seat_status text)""")
        self.conn.commit()
        self.current_class = -1

    def process_item(self, item, spider):
        if item.item_type == "course":
            self.process_class(item)
        elif item.item_type == "section":
            self.process_section(item)
        return item

    def process_class(self, item):
        c = self.conn.cursor()
        c.execute("select rowid from courses where department = ? and course_num = ?",
                  (item['department'], item['course_num']))
        new_id = c.fetchone()
        if new_id is None:
            c.execute("insert into courses values (?,?,?,?,?,?,?,?)",
                      (item['department'],
                       item['course_num'],
                       item['course_title'],
                       item['credits'],
                       item['desc'],
                       item['last_taught'],
                       item['description'],
                       item['pReq'])
            )
            self.conn.commit()
            c.execute("select rowid from courses where department = ? and course_num = ?",
                      (item['department'], item['course_num']))
            new_id = c.fetchone()
        self.current_class = new_id[0]

    def process_section(self, item):
        c = self.conn.cursor()
        c.execute("select rowid from sections where class_no = ? and last_updated = ?", (item['class_no'], item['last_updated']))
        if c.fetchone() is not None:
            return
        c.execute("insert into sections values (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                  (item['department'],
                   item['course_num'],
                   item['course_title'],
                   item['last_updated'],
                   item['class_no'],
                   item['sec_no'],
                   item['session'],
                   item['time'],
                   item['place'],
                   item['teacher'],
                   item['credits'],
                   item['openSeats'],
                   item['seat_status'])
        )
        self.conn.commit()
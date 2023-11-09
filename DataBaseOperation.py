import psycopg2
from datetime import datetime

class DBOperation():

    def __init__(self):
        connection_string = "postgresql://vpms_user:RUrfhs9jSEZz9uRM0HzW1iqWPx9XCIZF@dpg-cl4p7fs2np1s7383qb7g-a.singapore-postgres.render.com/vpms"

        try:
            self.connection = psycopg2.connect(connection_string)
            print("Connected to the DB")
        except Exception as e:
            print(f"Error: {e}")

    def InsertOneTimeData(self, space_for_two, space_for_four):
        cursor = self.connection.cursor()
        for x in range(space_for_two):
            cursor.execute("INSERT into slots (space_for, is_empty) values (2, 1)")
            self.connection.commit()

        for x in range(space_for_four):
            cursor.execute("INSERT into slots (space_for, is_empty) values (4, 1)")
            self.connection.commit()
        cursor.close()

    def ChangeSlots(self , space_for_two , space_for_four):
        cursor = self.connection.cursor()
        cursor.execute("TRUNCATE table slots")
        
        for x in range(space_for_two):
            a = 200 + x
            cursor.execute(f"INSERT into slots (id , space_for, is_empty) values ({a} ,2, 1)")
            self.connection.commit()

        for x in range(space_for_four):
            b = 400 + x
            cursor.execute(f"INSERT into slots (id , space_for, is_empty) values ({b} , 4 , 1)")
            self.connection.commit()
        cursor.close()

    def InsertAdmin(self, username, password):
        cursor = self.connection.cursor()
        val = (username, password)
        cursor.execute("INSERT into admin (username, password) values (%s, %s)", val)
        self.connection.commit()
        cursor.close()

    def doAdminLogin(self, username, password):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM admin WHERE username=%s AND password=%s", (username, password))
        data = cursor.fetchall()
        cursor.close()
        if len(data) > 0:
            return True
        else:
            return False

    def getSlotSpace(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM slots")
        data = cursor.fetchall()
        cursor.close()
        return data

    def getCurrentVehicle(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM vehicles WHERE is_exit='0'")
        data = cursor.fetchall()
        cursor.close()
        return data

    def getAllVehicle(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM vehicles WHERE is_exit='1'")
        data = cursor.fetchall()
        cursor.close()
        return data

    def AddVehicles(self, name, vehicle_no, mobile, vehicle_type):
        cursor = self.connection.cursor()
        
        cursor.execute("SELECT id FROM vehicles WHERE vehicle_no=%s AND is_exit='0'", (str(vehicle_no),))
        existing_vehicle = cursor.fetchone()

        if existing_vehicle:
            cursor.close()
            return "Vehicle with the same number is already parked and not exited"

        spacid = self.spaceAvailable(vehicle_type)

        if spacid:
            currentdata = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data = (name, mobile, currentdata, '', '0', vehicle_no, currentdata, currentdata, vehicle_type)

            cursor.execute("INSERT into vehicles (name, mobile, entry_time, exit_time, is_exit, vehicle_no, created_at, updated_at, vehicle_type) values (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id", data)
            self.connection.commit()
            lastid = cursor.fetchone()[0]
            
            cursor.execute("UPDATE slots SET vehicle_id=%s, is_empty=0 WHERE id=%s", (lastid, spacid))
            self.connection.commit()
            cursor.close()
            return True
        else:
            cursor.close()
            return "No Space Available for Parking"


    def spaceAvailable(self, v_type):
        cursor = self.connection.cursor()
        cursor.execute("SELECT id FROM slots WHERE is_empty=1 AND space_for=%s", (v_type,))
        data = cursor.fetchone()
        cursor.close()
        if data:
            return data[0]
        else:
            return False

    def exitVehicle(self, id):
        cursor = self.connection.cursor()
        currentdata = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("UPDATE slots SET is_empty=1, vehicle_id=NULL WHERE vehicle_id=%s", (id,))
        self.connection.commit()
        cursor.execute("UPDATE vehicles SET is_exit='1', exit_time=%s WHERE id=%s", (currentdata, id))
        self.connection.commit()
        cursor.close()

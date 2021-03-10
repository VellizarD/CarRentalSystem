import json

class Car:
	def __init__(self, brand: str, model: str, consumption: float, licenseNumber: str, ratePerHour: float, ratePerDay: float, ratePerWeek: float, status: str):
		self.ratePerDay = ratePerDay
		self.ratePerHour = ratePerHour
		self.ratePerWeek = ratePerWeek
		self.licenseNumber = licenseNumber
		self.consumption = consumption
		self.model = model
		self.brand = brand
		self.status = status

	def __str__(self):
		"""Prints detailed information about a car"""
		return "Brand: " + self.brand + "\tModel: " + self.model + "\tConsumption: " + str(self.consumption) + "\tLicense Number: " + self.licenseNumber + "\tRate Per Hour: " + str(self.ratePerHour) + "\tRate Per Day: " + str(self.ratePerDay) + "\tRate Per Week: " + str(
			self.ratePerWeek) + "\tStatus: " + self.status

	def printShort(self):
		"""Prints 'Brand', 'Model', 'Consumption', and 'License Number' values of a car"""
		print("Brand:", self.brand, "\nModel:", self.model, "\nConsumption:", self.consumption, "\nLicense Number:", self.licenseNumber, "\n")

	def updateStatus(self, status: str):
		self.status = status


class CarSerializer:
	@staticmethod
	def deserializeCatalogue() -> list:
		"""Reads the CarCatalogue JSON file and converts it into a list with elements of type Car and returns it"""
		with open('CarCatalogue.json') as file:
			data = json.load(file)
			tempList = list()
			for i in data:
				tempList.append(Car(i["brand"], i["model"], i["consumption"], i["licenseNumber"], i["ratePerHour"], i["ratePerDay"], i["ratePerWeek"], i["status"]))
		return tempList

	@staticmethod
	def deserializeRentedCarsDatabase() -> list:
		"""Reads the rentedCars JSON file and converts into a list of dictionaries and returns it"""
		with open("rentedCars.json") as file:
			data = json.load(file)
			tempList = list()
			for i in data:
				tempList.append(i)
		return tempList

	@staticmethod
	def serializeCarCatalogue(info: list[Car]):
		"""Saves any changes in the state of the cars into the CarCatalogue JSON file"""
		with open("CarCatalogue.json", "w") as file:
			tempList = list()
			for e in info:
				temp = {
					"brand": e.brand,
					"model": e.model,
					"consumption": e.consumption,
					"licenseNumber": e.licenseNumber,
					"ratePerHour": e.ratePerHour,
					"ratePerDay": e.ratePerDay,
					"ratePerWeek": e.ratePerWeek,
					"status": e.status}
				tempList.append(temp)
			json.dump(tempList, file)

	@staticmethod
	def serializeRentedCars(info: list):
		"""Saves any changes in the rentedCars list into the rentedCars JSON file"""
		with open("rentedCars.json", "w") as file:
			json.dump(info, file)


class System:
	def __init__(self):
		self.allCarsList = CarSerializer.deserializeCatalogue()
		self.rentedCarsList = CarSerializer.deserializeRentedCarsDatabase()
		self.availableCars = list()
		for car in self.allCarsList:
			if car.status == 'Available':
				self.availableCars.append(car)

	def removeFromRentedCarsList(self, car: Car):
		"""Removes a car from the rentedCarsList list variable"""
		for a in self.rentedCarsList:
			if a["licenseNumber"] == car.licenseNumber:
				self.rentedCarsList.remove(a)
		CarSerializer.serializeRentedCars(self.rentedCarsList)
		CarSerializer.serializeCarCatalogue(self.allCarsList)

	def addToRentedCarsList(self, client: str, car: Car, period: str, rate: float):
		"""Adds a car in the rentedCarsList list variable"""
		temp = {
			"licenseNumber": car.licenseNumber,
			"clientName": client,
			"rentalPeriod": period,
			"price": rate
		}
		self.rentedCarsList.append(temp)
		CarSerializer.serializeRentedCars(self.rentedCarsList)

	def findCar(self, number: str) -> Car:
		"""Finds a car with the provided License Number in the allCarsList list and returns it"""
		for car in self.allCarsList:
			if car.licenseNumber == number:
				return car


class Client:
	def __init__(self, name: str, system: System):
		self.sessionCounter = 0
		self.system = system
		self.name = name
		self.currentlyRentedCars = list()
		for el in CarSerializer.deserializeRentedCarsDatabase():
			if el['clientName'] == name:
				self.currentlyRentedCars.append(el)
		self.priceToPay = self.checkClientsCurrentPrice()

	def getCurrentlyRentedCars(self):
		"""Prints short information about every car that is currently rented by the user"""
		for i in self.currentlyRentedCars:
			for j in self.system.allCarsList:
				if i['licenseNumber'] == j.licenseNumber:
					j.printShort()

	def checkClientsCurrentPrice(self) -> float:
		"""Returns the total price the user has to pay at the moment"""
		tempPrice = 0
		for car in self.currentlyRentedCars:
			tempPrice += car["price"]
		return tempPrice

	def returnCar(self, _licenseNumber: str):
		"""Counts the car with a specific LicenseNumber as returned, changes the car' status to 'Available', then subtracts its price from the total price"""
		for elem in self.currentlyRentedCars:
			if elem["licenseNumber"].__eq__(_licenseNumber):
				carTemp = self.system.findCar(_licenseNumber)
				carTemp.updateStatus("Available")
				carTemp.printShort()
				self.currentlyRentedCars.remove(elem)
				self.system.removeFromRentedCarsList(carTemp)

	def rentCarForDay(self, car: Car):
		"""Rents the specified car for a day, changes its state to 'Rented', adds it to the currentlyRentedCars list with rentalPeriod set to 'Day', and adds its ratePerDay value to the total price"""
		if car.status.__eq__('Rented'):
			print("This car is currently unavailable!")
		else:
			self.sessionCounter += 1
			car.updateStatus("Rented")
			for i in self.system.allCarsList:
				if i.licenseNumber == car.licenseNumber:
					i.status = "Rented"
			print("You'll have to pay: ", car.ratePerDay, "per day!", end="")
			if self.sessionCounter == 3:
				rate = car.ratePerDay - car.ratePerDay * 0.3
				print("\nCongratulations! You just rented your 3rd car for the session. You get 30% off for the last rented car! ")
				print("Price with 30% discount:", rate)
			else:
				rate = car.ratePerDay
			self.currentlyRentedCars.append({
				"licenseNumber": car.licenseNumber,
				"clientName": self.name,
				"rentalPeriod": "Day",
				"price": rate
			})
			self.system.addToRentedCarsList(self.name, car, "Day", rate)
			CarSerializer.serializeCarCatalogue(self.system.allCarsList)
			CarSerializer.serializeRentedCars(self.system.rentedCarsList)

	def rentCarForHour(self, car: Car, hours: int):
		"""Rents the specified car for the specified number of hours, changes its state to 'Rented', adds it to the currentlyRentedCars list with rentalPeriod set to 'Hour' and the specified number of hours, and adds its ratePerHour value multiplied to the number of hours  to the total price"""
		if car.status.__eq__('Rented'):
			print("This car is currently unavailable!")
		else:
			self.sessionCounter += 1
			car.updateStatus("Rented")
			for i in self.system.allCarsList:
				if i.licenseNumber == car.licenseNumber:
					i.status = "Rented"
			print("You'll have to pay: ", car.ratePerHour, "per hour, total: ")
			print(car.ratePerHour * hours)
			if self.sessionCounter == 3:
				rate = car.ratePerHour * hours - car.ratePerHour * hours * 0.3
				print("\nCongratulations! You just rented your 3rd car for the session. You get 30% off for the last rented car! ")
				print("Price with 30% discount:", rate)
			else:
				rate = car.ratePerHour * hours
			self.currentlyRentedCars.append({
				"licenseNumber": car.licenseNumber,
				"clientName": self.name,
				"rentalPeriod": "Hour",
				"price": rate
			})
			self.system.addToRentedCarsList(self.name, car, "Hour", rate)
			CarSerializer.serializeCarCatalogue(self.system.allCarsList)
			CarSerializer.serializeRentedCars(self.system.rentedCarsList)

	def rentCarForWeek(self, car: Car):
		"""Rents the specified car for a week, changes its state to 'Rented', adds it to the currentlyRentedCars list with rentalPeriod set to 'Week', and adds its ratePerWeek value to the total price"""
		if car.status.__eq__('Rented'):
			print("This car is currently unavailable!")
		else:
			self.sessionCounter += 1
			car.updateStatus("Rented")
			for i in self.system.allCarsList:
				if i.licenseNumber == car.licenseNumber:
					i.status = "Rented"
			print("You'll have to pay: ", car.ratePerWeek, "per week!")
			if self.sessionCounter == 3:
				rate = car.ratePerWeek - car.ratePerWeek * 0.3
				print("\nCongratulations! You just rented your 3rd car for the session. You get 30% off for the last rented car! ")
				print("Price with 30% discount:", rate)
			else:
				rate = car.ratePerWeek
			self.currentlyRentedCars.append({
				"licenseNumber": car.licenseNumber,
				"clientName": self.name,
				"rentalPeriod": "Week",
				"price": rate
			})
			self.system.addToRentedCarsList(self.name, car, "Week", rate)
			CarSerializer.serializeCarCatalogue(self.system.allCarsList)
			CarSerializer.serializeRentedCars(self.system.rentedCarsList)


def main():
	clientName = input("Hello, please input your name: ")
	print("Welcome", clientName, ", please choose from the following options: ")
	system = System()
	client = Client(clientName, system)
	print('1: See all available cars', '\n2: Rent a car for an hour', '\n3: Rent a car for a day', '\n4: Rent a car for a week', '\n5: See all cars rented by You', '\n6: See total of Your rentals ', '\n7: Return a car', '\n8: Exit System')
	while True:
		try:
			choice = int(input('Enter Commands Bellow: \n'))
		except ValueError:
			print("Please Enter a Valid Command")
			continue
		break

	while choice != 8:
		if choice == 1:
			system = System()
			for car in system.availableCars:
				print(str(car))
		elif choice == 2:
			number = input("Please input the license number of the car you want to rent for an hour: ")
			doesCarExist = False
			for el in system.availableCars:
				if el.licenseNumber.__eq__(number):
					doesCarExist = True
			if not doesCarExist:
				print("This car is currently unavailable or does not exist!")
			else:
				hours = input("Please input how many hours do you want to rent the car for: ")
				while not hours.isdigit():
					print("Invalid input!")
					hours = input("Please input how many hours do you want to rent the car for: ")
				carToRent = system.findCar(number)
				client.rentCarForHour(carToRent, int(hours))
		elif choice == 3:
			number = input("Please input the license number of the car you want to rent for a day: ")
			doesCarExist = False
			for el in system.availableCars:
				if el.licenseNumber.__eq__(number):
					doesCarExist = True
			if not doesCarExist:
				print("This car is currently unavailable or does not exist!")
			else:
				carToRent = system.findCar(number)
				client.rentCarForDay(carToRent)
		elif choice == 4:
			number = input("Please input the license number of the car you want to rent for a week: ")
			doesCarExist = False
			for el in system.availableCars:
				if el.licenseNumber.__eq__(number):
					doesCarExist = True
			if not doesCarExist:
				print("This car is currently unavailable or does not exist!")
			else:
				carToRent = system.findCar(number)
				client.rentCarForWeek(carToRent)
		elif choice == 5:
			client.getCurrentlyRentedCars()
		elif choice == 6:
			print("Current total:", client.checkClientsCurrentPrice())
		elif choice == 7:
			num = input("Please input the license number of the car You want to return: ")
			client.returnCar(num)
		else:
			print("Please Enter a Valid Command!")
		try:
			choice = int(input(" "))
		except ValueError:
			print("Please Enter a Valid Command")
	print("Have a good day!")


if __name__ == "__main__":
	main()

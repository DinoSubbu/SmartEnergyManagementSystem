var faker = require('faker');

var database = { customers: []};

for (var i = 1; i<= 100; i++) {
  database.customers.push({
    id: i,
    name: faker.name.firstName() + ' ' + faker.name.lastName(),
  });
}

console.log(JSON.stringify(database));
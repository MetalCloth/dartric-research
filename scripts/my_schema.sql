-- Table: customers
CREATE TABLE customers (
	customer_id VARCHAR(5) NOT NULL, 
	company_name VARCHAR(40) NOT NULL, 
	contact_name VARCHAR(30), 
	contact_title VARCHAR(30), 
	address VARCHAR(60), 
	city VARCHAR(15), 
	region VARCHAR(15), 
	postal_code VARCHAR(10), 
	country VARCHAR(15), 
	phone VARCHAR(24), 
	fax VARCHAR(24), 
	CONSTRAINT pk_customers PRIMARY KEY (customer_id)
);

-- Table: orders
CREATE TABLE orders (
	order_id SMALLINT NOT NULL, 
	customer_id VARCHAR(5), 
	employee_id SMALLINT, 
	order_date DATE, 
	required_date DATE, 
	shipped_date DATE, 
	ship_via SMALLINT, 
	freight REAL, 
	ship_name VARCHAR(40), 
	ship_address VARCHAR(60), 
	ship_city VARCHAR(15), 
	ship_region VARCHAR(15), 
	ship_postal_code VARCHAR(10), 
	ship_country VARCHAR(15), 
	CONSTRAINT pk_orders PRIMARY KEY (order_id), 
	CONSTRAINT fk_orders_customers FOREIGN KEY(customer_id) REFERENCES customers (customer_id), 
	CONSTRAINT fk_orders_employees FOREIGN KEY(employee_id) REFERENCES employees (employee_id), 
	CONSTRAINT fk_orders_shippers FOREIGN KEY(ship_via) REFERENCES shippers (shipper_id)
);

-- Table: employees
CREATE TABLE employees (
	employee_id SMALLINT NOT NULL, 
	last_name VARCHAR(20) NOT NULL, 
	first_name VARCHAR(10) NOT NULL, 
	title VARCHAR(30), 
	title_of_courtesy VARCHAR(25), 
	birth_date DATE, 
	hire_date DATE, 
	address VARCHAR(60), 
	city VARCHAR(15), 
	region VARCHAR(15), 
	postal_code VARCHAR(10), 
	country VARCHAR(15), 
	home_phone VARCHAR(24), 
	extension VARCHAR(4), 
	photo BYTEA, 
	notes TEXT, 
	reports_to SMALLINT, 
	photo_path VARCHAR(255), 
	CONSTRAINT pk_employees PRIMARY KEY (employee_id), 
	CONSTRAINT fk_employees_employees FOREIGN KEY(reports_to) REFERENCES employees (employee_id)
);

-- Table: shippers
CREATE TABLE shippers (
	shipper_id SMALLINT NOT NULL, 
	company_name VARCHAR(40) NOT NULL, 
	phone VARCHAR(24), 
	CONSTRAINT pk_shippers PRIMARY KEY (shipper_id)
);

-- Table: us_states
CREATE TABLE us_states (
	state_id SMALLINT NOT NULL, 
	state_name VARCHAR(100), 
	state_abbr VARCHAR(2), 
	state_region VARCHAR(50), 
	CONSTRAINT pk_usstates PRIMARY KEY (state_id)
);

-- Table: products
CREATE TABLE products (
	product_id SMALLINT NOT NULL, 
	product_name VARCHAR(40) NOT NULL, 
	supplier_id SMALLINT, 
	category_id SMALLINT, 
	quantity_per_unit VARCHAR(20), 
	unit_price REAL, 
	units_in_stock SMALLINT, 
	units_on_order SMALLINT, 
	reorder_level SMALLINT, 
	discontinued INTEGER NOT NULL, 
	CONSTRAINT pk_products PRIMARY KEY (product_id), 
	CONSTRAINT fk_products_categories FOREIGN KEY(category_id) REFERENCES categories (category_id), 
	CONSTRAINT fk_products_suppliers FOREIGN KEY(supplier_id) REFERENCES suppliers (supplier_id)
);

-- Table: categories
CREATE TABLE categories (
	category_id SMALLINT NOT NULL, 
	category_name VARCHAR(15) NOT NULL, 
	description TEXT, 
	picture BYTEA, 
	CONSTRAINT pk_categories PRIMARY KEY (category_id)
);

-- Table: suppliers
CREATE TABLE suppliers (
	supplier_id SMALLINT NOT NULL, 
	company_name VARCHAR(40) NOT NULL, 
	contact_name VARCHAR(30), 
	contact_title VARCHAR(30), 
	address VARCHAR(60), 
	city VARCHAR(15), 
	region VARCHAR(15), 
	postal_code VARCHAR(10), 
	country VARCHAR(15), 
	phone VARCHAR(24), 
	fax VARCHAR(24), 
	homepage TEXT, 
	CONSTRAINT pk_suppliers PRIMARY KEY (supplier_id)
);

-- Table: order_details
CREATE TABLE order_details (
	order_id SMALLINT NOT NULL, 
	product_id SMALLINT NOT NULL, 
	unit_price REAL NOT NULL, 
	quantity SMALLINT NOT NULL, 
	discount REAL NOT NULL, 
	CONSTRAINT pk_order_details PRIMARY KEY (order_id, product_id), 
	CONSTRAINT fk_order_details_orders FOREIGN KEY(order_id) REFERENCES orders (order_id), 
	CONSTRAINT fk_order_details_products FOREIGN KEY(product_id) REFERENCES products (product_id)
);

-- Table: region
CREATE TABLE region (
	region_id SMALLINT NOT NULL, 
	region_description VARCHAR(60) NOT NULL, 
	CONSTRAINT pk_region PRIMARY KEY (region_id)
);

-- Table: territories
CREATE TABLE territories (
	territory_id VARCHAR(20) NOT NULL, 
	territory_description VARCHAR(60) NOT NULL, 
	region_id SMALLINT NOT NULL, 
	CONSTRAINT pk_territories PRIMARY KEY (territory_id), 
	CONSTRAINT fk_territories_region FOREIGN KEY(region_id) REFERENCES region (region_id)
);

-- Table: employee_territories
CREATE TABLE employee_territories (
	employee_id SMALLINT NOT NULL, 
	territory_id VARCHAR(20) NOT NULL, 
	CONSTRAINT pk_employee_territories PRIMARY KEY (employee_id, territory_id), 
	CONSTRAINT fk_employee_territories_employees FOREIGN KEY(employee_id) REFERENCES employees (employee_id), 
	CONSTRAINT fk_employee_territories_territories FOREIGN KEY(territory_id) REFERENCES territories (territory_id)
);

-- Table: customer_demographics
CREATE TABLE customer_demographics (
	customer_type_id VARCHAR(5) NOT NULL, 
	customer_desc TEXT, 
	CONSTRAINT pk_customer_demographics PRIMARY KEY (customer_type_id)
);

-- Table: customer_customer_demo
CREATE TABLE customer_customer_demo (
	customer_id VARCHAR(5) NOT NULL, 
	customer_type_id VARCHAR(5) NOT NULL, 
	CONSTRAINT pk_customer_customer_demo PRIMARY KEY (customer_id, customer_type_id), 
	CONSTRAINT fk_customer_customer_demo_customer_demographics FOREIGN KEY(customer_type_id) REFERENCES customer_demographics (customer_type_id), 
	CONSTRAINT fk_customer_customer_demo_customers FOREIGN KEY(customer_id) REFERENCES customers (customer_id)
);

-- Table: payment
CREATE TABLE payment (
	payment_id SERIAL NOT NULL, 
	customer_id INTEGER NOT NULL, 
	staff_id INTEGER NOT NULL, 
	rental_id INTEGER NOT NULL, 
	amount NUMERIC(5, 2) NOT NULL, 
	payment_date TIMESTAMP WITH TIME ZONE NOT NULL, 
	CONSTRAINT payment_pkey PRIMARY KEY (payment_id, payment_date)
);

-- Table: payment_p2022_07
CREATE TABLE payment_p2022_07 (
	payment_id SERIAL NOT NULL, 
	customer_id INTEGER NOT NULL, 
	staff_id INTEGER NOT NULL, 
	rental_id INTEGER NOT NULL, 
	amount NUMERIC(5, 2) NOT NULL, 
	payment_date TIMESTAMP WITH TIME ZONE NOT NULL, 
	CONSTRAINT payment_p2022_07_pkey PRIMARY KEY (payment_id, payment_date)
);

-- Table: film
CREATE TABLE film (
	film_id SERIAL NOT NULL, 
	title TEXT NOT NULL, 
	description TEXT, 
	release_year year, 
	language_id INTEGER NOT NULL, 
	original_language_id INTEGER, 
	rental_duration SMALLINT DEFAULT 3 NOT NULL, 
	rental_rate NUMERIC(4, 2) DEFAULT 4.99 NOT NULL, 
	length SMALLINT, 
	replacement_cost NUMERIC(5, 2) DEFAULT 19.99 NOT NULL, 
	rating mpaa_rating DEFAULT 'G'::mpaa_rating, 
	last_update TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	special_features TEXT[], 
	fulltext TSVECTOR NOT NULL, 
	CONSTRAINT film_pkey PRIMARY KEY (film_id), 
	CONSTRAINT film_language_id_fkey FOREIGN KEY(language_id) REFERENCES language (language_id) ON DELETE RESTRICT ON UPDATE CASCADE, 
	CONSTRAINT film_original_language_id_fkey FOREIGN KEY(original_language_id) REFERENCES language (language_id) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Table: language
CREATE TABLE language (
	language_id SERIAL NOT NULL, 
	name CHAR(20) NOT NULL, 
	last_update TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT language_pkey PRIMARY KEY (language_id)
);

-- Table: actor
CREATE TABLE actor (
	actor_id SERIAL NOT NULL, 
	first_name TEXT NOT NULL, 
	last_name TEXT NOT NULL, 
	last_update TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT actor_pkey PRIMARY KEY (actor_id)
);

-- Table: address
CREATE TABLE address (
	address_id SERIAL NOT NULL, 
	address TEXT NOT NULL, 
	address2 TEXT, 
	district TEXT NOT NULL, 
	city_id INTEGER NOT NULL, 
	postal_code TEXT, 
	phone TEXT NOT NULL, 
	last_update TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT address_pkey PRIMARY KEY (address_id), 
	CONSTRAINT address_city_id_fkey FOREIGN KEY(city_id) REFERENCES city (city_id) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Table: city
CREATE TABLE city (
	city_id SERIAL NOT NULL, 
	city TEXT NOT NULL, 
	country_id INTEGER NOT NULL, 
	last_update TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT city_pkey PRIMARY KEY (city_id), 
	CONSTRAINT city_country_id_fkey FOREIGN KEY(country_id) REFERENCES country (country_id) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Table: country
CREATE TABLE country (
	country_id SERIAL NOT NULL, 
	country TEXT NOT NULL, 
	last_update TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT country_pkey PRIMARY KEY (country_id)
);

-- Table: category
CREATE TABLE category (
	category_id SERIAL NOT NULL, 
	name TEXT NOT NULL, 
	last_update TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT category_pkey PRIMARY KEY (category_id)
);

-- Table: customer
CREATE TABLE customer (
	customer_id SERIAL NOT NULL, 
	store_id INTEGER NOT NULL, 
	first_name TEXT NOT NULL, 
	last_name TEXT NOT NULL, 
	email TEXT, 
	address_id INTEGER NOT NULL, 
	activebool BOOLEAN DEFAULT true NOT NULL, 
	create_date DATE DEFAULT CURRENT_DATE NOT NULL, 
	last_update TIMESTAMP WITH TIME ZONE DEFAULT now(), 
	active INTEGER, 
	CONSTRAINT customer_pkey PRIMARY KEY (customer_id), 
	CONSTRAINT customer_address_id_fkey FOREIGN KEY(address_id) REFERENCES address (address_id) ON DELETE RESTRICT ON UPDATE CASCADE, 
	CONSTRAINT customer_store_id_fkey FOREIGN KEY(store_id) REFERENCES store (store_id) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Table: store
CREATE TABLE store (
	store_id SERIAL NOT NULL, 
	manager_staff_id INTEGER NOT NULL, 
	address_id INTEGER NOT NULL, 
	last_update TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT store_pkey PRIMARY KEY (store_id), 
	CONSTRAINT store_address_id_fkey FOREIGN KEY(address_id) REFERENCES address (address_id) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Table: film_actor
CREATE TABLE film_actor (
	actor_id INTEGER NOT NULL, 
	film_id INTEGER NOT NULL, 
	last_update TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT film_actor_pkey PRIMARY KEY (actor_id, film_id), 
	CONSTRAINT film_actor_actor_id_fkey FOREIGN KEY(actor_id) REFERENCES actor (actor_id) ON DELETE RESTRICT ON UPDATE CASCADE, 
	CONSTRAINT film_actor_film_id_fkey FOREIGN KEY(film_id) REFERENCES film (film_id) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Table: film_category
CREATE TABLE film_category (
	film_id INTEGER NOT NULL, 
	category_id INTEGER NOT NULL, 
	last_update TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT film_category_pkey PRIMARY KEY (film_id, category_id), 
	CONSTRAINT film_category_category_id_fkey FOREIGN KEY(category_id) REFERENCES category (category_id) ON DELETE RESTRICT ON UPDATE CASCADE, 
	CONSTRAINT film_category_film_id_fkey FOREIGN KEY(film_id) REFERENCES film (film_id) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Table: inventory
CREATE TABLE inventory (
	inventory_id SERIAL NOT NULL, 
	film_id INTEGER NOT NULL, 
	store_id INTEGER NOT NULL, 
	last_update TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT inventory_pkey PRIMARY KEY (inventory_id), 
	CONSTRAINT inventory_film_id_fkey FOREIGN KEY(film_id) REFERENCES film (film_id) ON DELETE RESTRICT ON UPDATE CASCADE, 
	CONSTRAINT inventory_store_id_fkey FOREIGN KEY(store_id) REFERENCES store (store_id) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Table: rental
CREATE TABLE rental (
	rental_id SERIAL NOT NULL, 
	rental_date TIMESTAMP WITH TIME ZONE NOT NULL, 
	inventory_id INTEGER NOT NULL, 
	customer_id INTEGER NOT NULL, 
	return_date TIMESTAMP WITH TIME ZONE, 
	staff_id INTEGER NOT NULL, 
	last_update TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT rental_pkey PRIMARY KEY (rental_id), 
	CONSTRAINT rental_customer_id_fkey FOREIGN KEY(customer_id) REFERENCES customer (customer_id) ON DELETE RESTRICT ON UPDATE CASCADE, 
	CONSTRAINT rental_inventory_id_fkey FOREIGN KEY(inventory_id) REFERENCES inventory (inventory_id) ON DELETE RESTRICT ON UPDATE CASCADE, 
	CONSTRAINT rental_staff_id_fkey FOREIGN KEY(staff_id) REFERENCES staff (staff_id) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Table: staff
CREATE TABLE staff (
	staff_id SERIAL NOT NULL, 
	first_name TEXT NOT NULL, 
	last_name TEXT NOT NULL, 
	address_id INTEGER NOT NULL, 
	email TEXT, 
	store_id INTEGER NOT NULL, 
	active BOOLEAN DEFAULT true NOT NULL, 
	username TEXT NOT NULL, 
	password TEXT, 
	last_update TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	picture BYTEA, 
	CONSTRAINT staff_pkey PRIMARY KEY (staff_id), 
	CONSTRAINT staff_address_id_fkey FOREIGN KEY(address_id) REFERENCES address (address_id) ON DELETE RESTRICT ON UPDATE CASCADE, 
	CONSTRAINT staff_store_id_fkey FOREIGN KEY(store_id) REFERENCES store (store_id)
);

-- Table: payment_p2022_01
CREATE TABLE payment_p2022_01 (
	payment_id SERIAL NOT NULL, 
	customer_id INTEGER NOT NULL, 
	staff_id INTEGER NOT NULL, 
	rental_id INTEGER NOT NULL, 
	amount NUMERIC(5, 2) NOT NULL, 
	payment_date TIMESTAMP WITH TIME ZONE NOT NULL, 
	CONSTRAINT payment_p2022_01_pkey PRIMARY KEY (payment_id, payment_date), 
	CONSTRAINT payment_p2022_01_customer_id_fkey FOREIGN KEY(customer_id) REFERENCES customer (customer_id), 
	CONSTRAINT payment_p2022_01_rental_id_fkey FOREIGN KEY(rental_id) REFERENCES rental (rental_id), 
	CONSTRAINT payment_p2022_01_staff_id_fkey FOREIGN KEY(staff_id) REFERENCES staff (staff_id)
);

-- Table: payment_p2022_02
CREATE TABLE payment_p2022_02 (
	payment_id SERIAL NOT NULL, 
	customer_id INTEGER NOT NULL, 
	staff_id INTEGER NOT NULL, 
	rental_id INTEGER NOT NULL, 
	amount NUMERIC(5, 2) NOT NULL, 
	payment_date TIMESTAMP WITH TIME ZONE NOT NULL, 
	CONSTRAINT payment_p2022_02_pkey PRIMARY KEY (payment_id, payment_date), 
	CONSTRAINT payment_p2022_02_customer_id_fkey FOREIGN KEY(customer_id) REFERENCES customer (customer_id), 
	CONSTRAINT payment_p2022_02_rental_id_fkey FOREIGN KEY(rental_id) REFERENCES rental (rental_id), 
	CONSTRAINT payment_p2022_02_staff_id_fkey FOREIGN KEY(staff_id) REFERENCES staff (staff_id)
);

-- Table: payment_p2022_03
CREATE TABLE payment_p2022_03 (
	payment_id SERIAL NOT NULL, 
	customer_id INTEGER NOT NULL, 
	staff_id INTEGER NOT NULL, 
	rental_id INTEGER NOT NULL, 
	amount NUMERIC(5, 2) NOT NULL, 
	payment_date TIMESTAMP WITH TIME ZONE NOT NULL, 
	CONSTRAINT payment_p2022_03_pkey PRIMARY KEY (payment_id, payment_date), 
	CONSTRAINT payment_p2022_03_customer_id_fkey FOREIGN KEY(customer_id) REFERENCES customer (customer_id), 
	CONSTRAINT payment_p2022_03_rental_id_fkey FOREIGN KEY(rental_id) REFERENCES rental (rental_id), 
	CONSTRAINT payment_p2022_03_staff_id_fkey FOREIGN KEY(staff_id) REFERENCES staff (staff_id)
);

-- Table: payment_p2022_04
CREATE TABLE payment_p2022_04 (
	payment_id SERIAL NOT NULL, 
	customer_id INTEGER NOT NULL, 
	staff_id INTEGER NOT NULL, 
	rental_id INTEGER NOT NULL, 
	amount NUMERIC(5, 2) NOT NULL, 
	payment_date TIMESTAMP WITH TIME ZONE NOT NULL, 
	CONSTRAINT payment_p2022_04_pkey PRIMARY KEY (payment_id, payment_date), 
	CONSTRAINT payment_p2022_04_customer_id_fkey FOREIGN KEY(customer_id) REFERENCES customer (customer_id), 
	CONSTRAINT payment_p2022_04_rental_id_fkey FOREIGN KEY(rental_id) REFERENCES rental (rental_id), 
	CONSTRAINT payment_p2022_04_staff_id_fkey FOREIGN KEY(staff_id) REFERENCES staff (staff_id)
);

-- Table: payment_p2022_05
CREATE TABLE payment_p2022_05 (
	payment_id SERIAL NOT NULL, 
	customer_id INTEGER NOT NULL, 
	staff_id INTEGER NOT NULL, 
	rental_id INTEGER NOT NULL, 
	amount NUMERIC(5, 2) NOT NULL, 
	payment_date TIMESTAMP WITH TIME ZONE NOT NULL, 
	CONSTRAINT payment_p2022_05_pkey PRIMARY KEY (payment_id, payment_date), 
	CONSTRAINT payment_p2022_05_customer_id_fkey FOREIGN KEY(customer_id) REFERENCES customer (customer_id), 
	CONSTRAINT payment_p2022_05_rental_id_fkey FOREIGN KEY(rental_id) REFERENCES rental (rental_id), 
	CONSTRAINT payment_p2022_05_staff_id_fkey FOREIGN KEY(staff_id) REFERENCES staff (staff_id)
);

-- Table: payment_p2022_06
CREATE TABLE payment_p2022_06 (
	payment_id SERIAL NOT NULL, 
	customer_id INTEGER NOT NULL, 
	staff_id INTEGER NOT NULL, 
	rental_id INTEGER NOT NULL, 
	amount NUMERIC(5, 2) NOT NULL, 
	payment_date TIMESTAMP WITH TIME ZONE NOT NULL, 
	CONSTRAINT payment_p2022_06_pkey PRIMARY KEY (payment_id, payment_date), 
	CONSTRAINT payment_p2022_06_customer_id_fkey FOREIGN KEY(customer_id) REFERENCES customer (customer_id), 
	CONSTRAINT payment_p2022_06_rental_id_fkey FOREIGN KEY(rental_id) REFERENCES rental (rental_id), 
	CONSTRAINT payment_p2022_06_staff_id_fkey FOREIGN KEY(staff_id) REFERENCES staff (staff_id)
);


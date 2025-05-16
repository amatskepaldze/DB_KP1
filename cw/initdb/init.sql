-- Создание таблиц
CREATE TABLE IF NOT EXISTS customer (
    customer_id bigint generated always as identity primary key,
    password varchar(100) not null check(length(password) >= 3),
    customer_login varchar(150) not null check(length(customer_login) >= 3),
    email varchar(100),
    rights varchar(10) not null
);

CREATE TABLE IF NOT EXISTS brand (
    brand_id bigint generated always as identity primary key,
    name varchar(100) not null,
    description text
);

CREATE TABLE IF NOT EXISTS category (
    category_id bigint generated always as identity primary key,
    name varchar(100) not null,
    description text
);

CREATE TABLE IF NOT EXISTS appliance (
    appliance_id bigint generated always as identity primary key,
    name varchar(100) not null,
    brand_id bigint not null references brand(brand_id),
    category_id bigint not null references category(category_id),
    price float not null,
    description text
);

CREATE TABLE IF NOT EXISTS shop (
    shop_id bigint generated always as identity primary key,
    address text not null
);

CREATE TABLE IF NOT EXISTS basket (
    basket_id bigint generated always as identity primary key,
    customer_id bigint not null references customer(customer_id),
    date date not null,
    status varchar(10) not null
);

CREATE TABLE IF NOT EXISTS appliance_pool (
    appliance_id bigint not null references appliance(appliance_id),
    basket_id bigint not null references basket(basket_id),
    quantity bigint not null
);

CREATE TABLE IF NOT EXISTS stock (
    appliance_id bigint not null references appliance(appliance_id),
    shop_id bigint not null references shop(shop_id),
    stock bigint not null
);

CREATE TABLE IF NOT EXISTS logging (
    log_id bigint generated always as identity primary key,
    timestamp timestamp not null default current_timestamp,
    customer_id bigint not null references customer(customer_id),
    action varchar(50) not null, 
    details text
);

CREATE TABLE IF NOT EXISTS orders (
    order_id bigint generated always as identity primary key,
    customer_id bigint not null references customer(customer_id),
    basket_id bigint not null references basket(basket_id),
    card_number varchar(16) not null check(length(card_number) = 16),
    card_holder_name varchar(100) not null,
    card_expiry_date date not null,
    card_cvv varchar(3) not null check(length(card_cvv) = 3)
);

-- Создание вьюшек
create or replace view appliance_in_basket
as select customer_id, appliance_pool.basket_id, appliance_pool.appliance_id, appliance.name appliance_name, brand_id, brand.name brand_name, price, quantity, status
from appliance_pool join basket using(basket_id)
join appliance using(appliance_id)
join brand using(brand_id);

create or replace view appliance_with_shop
as select appliance.appliance_id, appliance.name appliance_name, brand.name brand_name, category.name category_name, appliance.price, stock.stock, stock.shop_id, shop.address, appliance.description appliance_description, brand.description brand_description, category.description category_description
from appliance join brand using(brand_id)
join category using(category_id)
join stock using(appliance_id)
join shop using(shop_id);

-- Создание функции
CREATE OR REPLACE FUNCTION get_basket_price(basket_id integer) RETURNS FLOAT AS $$
	select sum(price * quantity) total
	from appliance_in_basket
	where appliance_in_basket.basket_id = basket_id
	group by basket_id
$$ LANGUAGE SQL;

-- Создание триггерных функций
CREATE OR REPLACE FUNCTION log_basket_changes() RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO logging (customer_id, action, details)
        VALUES (NEW.customer_id, 'CREATE_BASKET', 'Created a new basket');
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER basket_create_trigger
AFTER INSERT ON basket
FOR EACH ROW EXECUTE FUNCTION log_basket_changes();

CREATE OR REPLACE FUNCTION log_appliance_pool_changes()
RETURNS TRIGGER AS $$
declare
	user_id BIGINT;
begin
	select customer_id into user_id from basket where basket_id = new.basket_id and status = 'open';
    IF TG_OP = 'INSERT' then
        INSERT INTO logging (customer_id, action, details)
        VALUES (user_id, 'ADD_TO_BASKET', 'Added appliance with ID: ' || NEW.appliance_id || ' to basket with ID: ' || NEW.basket_id || ' (Quantity: ' || NEW.quantity || ')');
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO logging (customer_id, action, details)
        VALUES (user_id, 'UPDATE_BASKET', 'Added appliance with ID: ' || NEW.appliance_id || ' in basket with ID: ' || NEW.basket_id || ' (Added quantity: ' || NEW.quantity || ')');
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER appliance_pool_add_trigger
AFTER INSERT OR UPDATE ON appliance_pool
FOR EACH ROW EXECUTE FUNCTION log_appliance_pool_changes();

-- Создание юзера с возможностью чтения
CREATE ROLE slave_user WITH LOGIN PASSWORD 'qwerty';

-- Даем доступ на чтение таблиц
GRANT SELECT ON appliance TO slave_user;
GRANT SELECT ON appliance_pool TO slave_user;
GRANT SELECT ON basket TO slave_user;
GRANT SELECT ON brand TO slave_user;
GRANT SELECT ON category TO slave_user;
GRANT SELECT ON customer TO slave_user;
GRANT SELECT ON shop TO slave_user;
GRANT SELECT ON stock TO slave_user;
GRANT SELECT ON orders TO slave_user;

-- Даем доступ на чтение вьюшек
GRANT SELECT ON appliance_in_basket TO slave_user;
GRANT SELECT ON appliance_with_shop TO slave_user;

-- Даем доступ на исполнение функций
GRANT EXECUTE ON FUNCTION get_basket_price TO slave_user;
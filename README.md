# Python Crawler

```sql
CREATE TABLE public.pricerecommendation (
	productmaster_id int4 NULL,
	pricerecommendation float8 NULL,
	"date" timestamptz NULL
);
```

```sql
CREATE TABLE public.productmaster (
	id serial4 NOT NULL,
	"name" varchar NULL,
	detail varchar NULL,
	tokens _text NULL,
	occurrences _text NULL,
	CONSTRAINT productmaster_pkey PRIMARY KEY (id)
);
```

```sql
CREATE TABLE public.productprice (
	"_id" serial4 NOT NULL,
	"name" varchar NULL,
	price float8 NULL,
	originalprice float8 NULL,
	discountpercentage float8 NULL,
	detail varchar NULL,
	platform varchar NULL,
	productmaster_id int4 NULL,
	createdat varchar NULL,
	CONSTRAINT productprice_pkey PRIMARY KEY (_id)
);
```
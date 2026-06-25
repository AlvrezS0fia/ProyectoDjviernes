--
-- Base de datos: `clientes`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `auth_group`
--

CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL,
  `name` varchar(150) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `auth_group_permissions`
--

CREATE TABLE `auth_group_permissions` (
  `id` bigint(20) NOT NULL,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `auth_permission`
--

CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `auth_permission`
--

INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES
(1, 'Can add log entry', 1, 'add_logentry'),
(2, 'Can change log entry', 1, 'change_logentry'),
(3, 'Can delete log entry', 1, 'delete_logentry'),
(4, 'Can view log entry', 1, 'view_logentry'),
(5, 'Can add permission', 2, 'add_permission'),
(6, 'Can change permission', 2, 'change_permission'),
(7, 'Can delete permission', 2, 'delete_permission'),
(8, 'Can view permission', 2, 'view_permission'),
(9, 'Can add group', 3, 'add_group'),
(10, 'Can change group', 3, 'change_group'),
(11, 'Can delete group', 3, 'delete_group'),
(12, 'Can view group', 3, 'view_group'),
(13, 'Can add user', 4, 'add_user'),
(14, 'Can change user', 4, 'change_user'),
(15, 'Can delete user', 4, 'delete_user'),
(16, 'Can view user', 4, 'view_user'),
(17, 'Can add content type', 5, 'add_contenttype'),
(18, 'Can change content type', 5, 'change_contenttype'),
(19, 'Can delete content type', 5, 'delete_contenttype'),
(20, 'Can view content type', 5, 'view_contenttype'),
(21, 'Can add session', 6, 'add_session'),
(22, 'Can change session', 6, 'change_session'),
(23, 'Can delete session', 6, 'delete_session'),
(24, 'Can view session', 6, 'view_session'),
(25, 'Can add record', 7, 'add_record'),
(26, 'Can change record', 7, 'change_record'),
(27, 'Can delete record', 7, 'delete_record'),
(28, 'Can view record', 7, 'view_record');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `auth_user`
--

CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `auth_user`
--

INSERT INTO `auth_user` (`id`, `password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `email`, `is_staff`, `is_active`, `date_joined`) VALUES
(2, 'pbkdf2_sha256$600000$D1Foh9enMaNgFnz05KWyi9$UxDdoVzy5woDBL045/bw71FRujRekMmYyeMn8z5e4os=', '2026-06-12 18:37:28.348066', 1, 'lilliana', '', '', 'lilliana@gmail.com', 1, 1, '2026-04-27 12:06:21.161189'),
(3, 'pbkdf2_sha256$720000$jMPefCCotMz4466dOLmVrI$xnV1acwK2K3xmJHgVxEWoNqQIh2il4+MC9lM4igtiu4=', '2026-05-11 16:31:59.616952', 1, 'juan', 'juan', 'gallon', 'gallon@gmail.com', 1, 1, '2026-05-11 15:06:40.000000'),
(4, 'pbkdf2_sha256$720000$gm2RBj6hN9keEgcOf7sUOi$bnxj0aYPHHXIX4wOW3DI7+zqwsA9UvM9OE2Sp81TK+8=', NULL, 0, 'mariano', 'gomez', 'mendoza', 'mendoza@gmail.com', 0, 1, '2026-05-11 15:58:50.000000'),
(5, 'pbkdf2_sha256$600000$aGNpy0rV2Iqjdfn53aoKaY$2QwhhDJuvhTgZ83m0kqxNbZcWSNG5J/Kl6K6vp8x9Sc=', NULL, 1, 'adriana', 'adriana', 'uribe', 'uribe@gmail.com', 1, 1, '2026-05-15 21:41:43.000000'),
(6, 'pbkdf2_sha256$720000$iRJcYjcz1b2sQPW1GJIXDS$foUVWe0+hJDnxpXn7WemxLU2bGhHAyEVbc8uIJ3TPyo=', NULL, 1, 'charlarca', 'Samuel', 'chalarca', 'samuchamo@gmail.com', 1, 1, '2026-05-19 14:56:17.000000'),
(7, 'pbkdf2_sha256$720000$iIcnNGHCecP8Uz7hMHVuJf$4hQZOW4wZrOBHp5lKiXqpvFPM60E2k7vPHSTTWLSIeU=', '2026-06-02 13:08:46.039835', 0, 'camilas', '', '', '', 0, 1, '2026-06-02 13:08:45.375737'),
(8, 'pbkdf2_sha256$720000$gMON5bQp1oxUMrq1uh386z$qHuie4qxe2m0ol2OiYnU7g99zEdtxWZ2E7/LMCuVMA4=', '2026-06-02 13:57:24.840528', 0, 'luisa', '', '', '', 0, 1, '2026-06-02 13:54:46.124542'),
(9, 'pbkdf2_sha256$720000$ImaMZetESbcRObULC53EaE$2A2uNk3ectGZcSAtIsg++GxJZr/nUvkE2aXkkx1/V4w=', '2026-06-09 12:10:03.853253', 0, 'camila', 'camila', 'fernandez', 'camiliaf@gmail.com', 0, 1, '2026-06-05 18:32:41.590132'),
(10, 'pbkdf2_sha256$600000$UcgSlKyLzmOdNCJNKM3xK4$E1J4youMxVsMsZm3/ni2nKrS5pJc/+HHigdYCQjbAK0=', '2026-06-13 04:20:01.328573', 1, 'admin123', '', '', 'sofiaalvarezruiz279@gmail.com', 1, 1, '2026-06-13 04:18:22.158566');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `auth_user_groups`
--

CREATE TABLE `auth_user_groups` (
  `id` bigint(20) NOT NULL,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `auth_user_user_permissions`
--

CREATE TABLE `auth_user_user_permissions` (
  `id` bigint(20) NOT NULL,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `auth_user_user_permissions`
--

INSERT INTO `auth_user_user_permissions` (`id`, `user_id`, `permission_id`) VALUES
(1, 6, 1),
(4, 6, 6),
(3, 6, 9),
(2, 6, 11);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `django_admin_log`
--

CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext DEFAULT NULL,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) UNSIGNED NOT NULL CHECK (`action_flag` >= 0),
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `django_admin_log`
--

INSERT INTO `django_admin_log` (`id`, `action_time`, `object_id`, `object_repr`, `action_flag`, `change_message`, `content_type_id`, `user_id`) VALUES
(1, '2026-05-11 15:06:41.288948', '3', 'juan', 1, '[{\"added\": {}}]', 4, 2),
(2, '2026-05-11 15:07:25.819939', '3', 'juan', 2, '[{\"changed\": {\"fields\": [\"First name\", \"Last name\", \"Email address\", \"Staff status\", \"Superuser status\"]}}]', 4, 2),
(3, '2026-05-11 15:58:51.018723', '4', 'mariano', 1, '[{\"added\": {}}]', 4, 3),
(4, '2026-05-11 15:59:22.008871', '4', 'mariano', 2, '[{\"changed\": {\"fields\": [\"First name\", \"Last name\", \"Email address\"]}}]', 4, 3),
(5, '2026-05-15 21:41:43.754650', '5', 'adriana', 1, '[{\"added\": {}}]', 4, 2),
(6, '2026-05-15 21:42:13.849103', '5', 'adriana', 2, '[{\"changed\": {\"fields\": [\"First name\", \"Last name\", \"Email address\", \"Staff status\", \"Superuser status\"]}}]', 4, 2),
(7, '2026-05-15 22:04:07.971397', '3', 'mellia cachona melisacachona@gmail.com', 1, '[{\"added\": {}}]', 7, 2),
(8, '2026-05-15 22:05:18.995742', '3', 'mellia hermosa melisacachona@gmail.com', 2, '[{\"changed\": {\"fields\": [\"Last name\"]}}]', 7, 2),
(9, '2026-05-19 14:56:18.912431', '6', 'charlarca', 1, '[{\"added\": {}}]', 4, 2),
(10, '2026-05-19 14:58:36.567805', '6', 'charlarca', 2, '[{\"changed\": {\"fields\": [\"First name\", \"Last name\", \"Email address\", \"Staff status\", \"Superuser status\", \"User permissions\"]}}]', 4, 2),
(11, '2026-05-19 14:58:54.391121', '6', 'charlarca', 2, '[]', 4, 2),
(12, '2026-05-25 11:56:27.654572', '4', 'Sofia vargas agudelo', 2, '[{\"changed\": {\"fields\": [\"Last name\"]}}]', 7, 2),
(13, '2026-05-26 12:04:56.378770', '17', 'Jorge luis Ortiz', 2, '[{\"changed\": {\"fields\": [\"First name\"]}}]', 7, 2),
(14, '2026-05-26 12:05:08.432043', '1', 'Mateo Sueños', 3, '', 7, 2);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `django_content_type`
--

CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `django_content_type`
--

INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES
(1, 'admin', 'logentry'),
(3, 'auth', 'group'),
(2, 'auth', 'permission'),
(4, 'auth', 'user'),
(8, 'clientes', 'cliente'),
(5, 'contenttypes', 'contenttype'),
(6, 'sessions', 'session'),
(9, 'tienda', 'carritoitem'),
(10, 'tienda', 'favorito'),
(7, 'website', 'record');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `django_migrations`
--

CREATE TABLE `django_migrations` (
  `id` bigint(20) NOT NULL,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `django_migrations`
--

INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES
(1, 'contenttypes', '0001_initial', '2026-03-20 18:23:55.352908'),
(2, 'auth', '0001_initial', '2026-03-20 18:23:56.225977'),
(3, 'admin', '0001_initial', '2026-03-20 18:23:56.457920'),
(4, 'admin', '0002_logentry_remove_auto_add', '2026-03-20 18:23:56.480784'),
(5, 'admin', '0003_logentry_add_action_flag_choices', '2026-03-20 18:23:56.503155'),
(6, 'contenttypes', '0002_remove_content_type_name', '2026-03-20 18:23:56.637824'),
(7, 'auth', '0002_alter_permission_name_max_length', '2026-03-20 18:23:56.735417'),
(8, 'auth', '0003_alter_user_email_max_length', '2026-03-20 18:23:56.768760'),
(9, 'auth', '0004_alter_user_username_opts', '2026-03-20 18:23:56.792008'),
(10, 'auth', '0005_alter_user_last_login_null', '2026-03-20 18:23:56.905664'),
(11, 'auth', '0006_require_contenttypes_0002', '2026-03-20 18:23:56.910613'),
(12, 'auth', '0007_alter_validators_add_error_messages', '2026-03-20 18:23:56.934151'),
(13, 'auth', '0008_alter_user_username_max_length', '2026-03-20 18:23:56.965812'),
(14, 'auth', '0009_alter_user_last_name_max_length', '2026-03-20 18:23:56.993085'),
(15, 'auth', '0010_alter_group_name_max_length', '2026-03-20 18:23:57.021877'),
(16, 'auth', '0011_update_proxy_permissions', '2026-03-20 18:23:57.045721'),
(17, 'auth', '0012_alter_user_first_name_max_length', '2026-03-20 18:23:57.078674'),
(18, 'sessions', '0001_initial', '2026-03-20 18:23:57.147134'),
(19, 'website', '0001_initial', '2026-05-11 15:17:49.068474');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `django_session`
--

CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `django_session`
--

INSERT INTO `django_session` (`session_key`, `session_data`, `expire_date`) VALUES
('1a5hbabo3okmi7mqg9988ij47y17qyuk', '.eJxVjDsOwjAQBe_iGln-O1DS5wzWeneNA8iR4qRC3B0ipYD2zcx7iQTbWtPWeUkTiYsw4vS7ZcAHtx3QHdptlji3dZmy3BV50C7Hmfh5Pdy_gwq9fuuzJSAEEzUadmQ5I3v0CCEPmF3wFgrr6NCrCOwQHBZrBlWC0pkiiPcHHdQ5Nw:1wQ8M4:FT_Lqpip6rCwxVr3YgAgaLUDtKqRmZABzHTUOaYh95Q', '2026-06-04 18:42:48.408799'),
('28di2anguv04wn1hk5u4tiu3wpqctzys', '.eJxVjEEOwiAQAP_C2RCgSMGj976BLLuLVA0kpT0Z_25qetDrzGReIsK2lrh1XuJM4iK0EqdfmAAfXHdDd6i3JrHVdZmT3BN52C6nRvy8Hu3foEAv368nZ0MmNko7pQ1645H4HJKjnGBEhBwG9ooBrTeGRhxctp4Nae20eH8AD004Xw:1wYFqg:wTGbFXkeSVmzYm1dCkVxzGmZsPSSPUxqtmFLUNxniNs', '2026-06-27 04:19:58.932706'),
('2oefztf70l716trsb8hy4fnboh10h4bm', '.eJxVjDsOwjAQBe_iGlnGP9aU9DlDtOtdcADZUpxUiLtDpBTQvpl5LzXiupRx7TKPE6uzsurwuxHmh9QN8B3rrenc6jJPpDdF77TrobE8L7v7d1Cwl2-NDMwGrSM6EdgUonHOZ4lHEJIQPGHy0bKJBgKKSZAg-pD5Sj4yZPX-AOd7N90:1wMOoZ:We2SgkofHYJyD66QBKnKeDTLVf1HO7Ti1iBOlEO4mho', '2026-05-25 11:28:47.267078'),
('2qgg0cj20ihrhpatocrjo13ohbfgn4kf', '.eJxVjDsOwjAQBe_iGln-beSlpOcMltfe4ACypTipIu5OIqWA9s3M20SI61LC2nkOUxZXgeLyu1FML64HyM9YH02mVpd5Inko8qRd3lvm9-10_w5K7GWvncMhIzOYOEDGrLxxiDhSQkACAp92DEl5qw1bo0fLViM76x0p8OLzBdrRN0A:1wVZLX:B_BNrmI5aSOWSRe1cMPx6JcWatMTV239hLWMznSCJcY', '2026-06-19 18:32:43.539507'),
('2ssmnak84w8spimtu6i23nqbfo84hiw0', '.eJxVjM0OwiAQhN-FsyGsUH48evcZyG5ZpGogKe3J-O62SQ-azGm-b-YtIq5LiWvnOU5JXASI029HOD657iA9sN6bHFtd5onkrsiDdnlriV_Xw_07KNjLtnbBoQlWGYJBZ7Y2nbMJ5AOyCyHlgTNo8qwIUWFmTeBBe7VFMSQjPl_gNDfZ:1w556Q:ZOTN01hv_rwuXs2yql1PHJzDrDkY-RDRY9f1gYzHqY0', '2026-04-07 16:59:38.449165'),
('6hn4bdi8djwhcj1hqafy2ho0ggk5lrar', '.eJxVjMsOwiAQRf-FtSGFQodx6d5vIFNmkKqBpI-V8d-1SRe6veec-1KRtrXEbZE5TqzOyqrT7zZSekjdAd-p3ppOra7zNOpd0Qdd9LWxPC-H-3dQaCnfumPHlrA3ZAEHFE7epB4yeIDRdthTduI5o8sogZEATSCXKHRG8gDq_QHf8Df0:1wQV3x:TO9uemVhudHHurmw9qp-473dYhjqMYI8awOQyLwq1GM', '2026-06-05 18:57:37.608904'),
('8nyout5arsc0r4gwubu8fupamp75t6w3', '.eJxVjEEOwiAQRe_C2pCBQqe4dO8ZCMOAVA0kpV0Z765NutDtf-_9l_BhW4vfelr8zOIstDj9bhTiI9Ud8D3UW5Ox1XWZSe6KPGiX18bpeTncv4MSevnWCieVWDtAGxCIyKELkxp0goHAAGQ2rFHHTKySsdk4xxpwdNlG5FG8P8wkN3U:1wRYBp:wGf_QdYdHCPR2uRtS3WswHQaMka4HltcxyWhUOgtnd4', '2026-06-08 16:30:05.828378'),
('8t876u8cpkqq3jialmvwb9l7bpq4vpu9', '.eJxVjMEOwiAQBf-FsyEFlgU8eu83kKWAVA0kpT0Z_92Q9KDXNzPvzTwde_FHT5tfI7sywS6_W6DlmeoA8UH13vjS6r6tgQ-Fn7TzucX0up3u30GhXkYdSTorMugpyxQQEPMEaIRFbQxpEWJwQjoXyKBO2QFaC6gVWgUSFft8Acl1Nnk:1w9i1s:ryTgtdqZJ79kjyi_xNl-FXL953NnYWdA5YM5FrSdNcY', '2026-04-20 11:22:04.023420'),
('9a383qt2op3tb4xgefa01oj6bdup177s', 'e30:1wHO5U:OMiUr9wuM4TIyteymsMidOi2buHcEQjYxvtntZ8Aou4', '2026-05-11 15:41:32.291579'),
('9h1il8bswxfebhonjnpmdkbv732ywint', '.eJxVjM0OwiAQhN-FsyGsUH48evcZyG5ZpGogKe3J-O62SQ-azGm-b-YtIq5LiWvnOU5JXASI029HOD657iA9sN6bHFtd5onkrsiDdnlriV_Xw_07KNjLtnbBoQlWGYJBZ7Y2nbMJ5AOyCyHlgTNo8qwIUWFmTeBBe7VFMSQjPl_gNDfZ:1w553q:8YmVxu33tn5UTqY6qtBlFG4eDCnfAJfRgYhn97y-wQw', '2026-04-07 16:56:58.925032'),
('aqq8nk0cped9jzx65cf3h1lhsi2aeheg', '.eJxVjMEOwiAQRP-FsyGwQFc8eu83kIVFqRpISnsy_rtt0oPeJvPezFsEWpcS1p7nMLG4CBCn3y5Seua6A35QvTeZWl3mKcpdkQftcmycX9fD_Tso1Mu29t5nNA7cmVNMeoABrTbuppW1GTUBZWVZGdiiR_AmKY1EzM4ieUDx-QK0vTan:1wNzER:5nS8Kyq6LjqrHgb3D0UHjwxN4iE5culE-4DhyU75kDI', '2026-05-29 20:34:03.501526'),
('d09d9uu1ia6hf6iri2cbd3kd6zyov1f2', '.eJxVjDsOgzAQBe_iOrLwgn8p03MGa9e7xCQRSBiqKHcPSBRJ-2bmvVXCbS1pq7KkkdVVgbr8boT5KdMB-IHTfdZ5ntZlJH0o-qRV9zPL63a6fwcFa9nrAdnnjoTRY2yyA4zQQYRgmdiJFQjR-NCIgHehpV3DTHZw0JJhMurzBQR9OJA:1wHO8S:eNFNtYSvMLrojWI-WaMr7YHOsKBsjhxWj1rrRNbofSs', '2026-05-11 15:44:36.946383'),
('dh2t7qnpceiq3dil1l7326flklugc9st', '.eJxVjM0OwiAQhN-FsyGsUH48evcZyG5ZpGogKe3J-O62SQ-azGm-b-YtIq5LiWvnOU5JXASI029HOD657iA9sN6bHFtd5onkrsiDdnlriV_Xw_07KNjLtnbBoQlWGYJBZ7Y2nbMJ5AOyCyHlgTNo8qwIUWFmTeBBe7VFMSQjPl_gNDfZ:1w54w0:8E0pviW7l3eDNzERpD1MXNYrx0Z_xw_ZDWZqArojNTw', '2026-04-07 16:48:52.211321'),
('e0ukj61e3kwvidk2xbr0oczkulk8lpwl', '.eJxVjDsOwjAQBe_iGln-O1DS5wzWeneNA8iR4qRC3B0ipYD2zcx7iQTbWtPWeUkTiYsw4vS7ZcAHtx3QHdptlji3dZmy3BV50C7Hmfh5Pdy_gwq9fuuzJSAEEzUadmQ5I3v0CCEPmF3wFgrr6NCrCOwQHBZrBlWC0pkiiPcHHdQ5Nw:1wPMwP:0KsBrQYz52DR8fouJHT5Dt21Ml9csQO-t_EyxLPpBSo', '2026-06-02 16:05:09.917232'),
('hacc05n9nieoyaosdomz3b5is1tmuaqg', '.eJxVjEEOwiAQRe_C2pBSZii4dN8zkAEGqRqalHZlvLtt0oVu_3vvv4WnbS1-a7z4KYmr6MXldwsUn1wPkB5U77OMc12XKchDkSdtcpwTv26n-3dQqJW9zoYc2cwQNSjTockhAwJZjJkihUE7xdBRUoB2VzBA76zWpJBZ8yA-X_E5N9E:1wRsyl:Ez2GmqWhJDKSU2srhTrzlAtvprJM8a7lnmrzmt91KHw', '2026-06-09 14:41:59.040311'),
('hqzf0jciy7ugulfychoen0qssfjbd7ph', '.eJxVjEEOwiAQRe_C2pBSZii4dN8zkAEGqRqalHZlvLtt0oVu_3vvv4WnbS1-a7z4KYmr6MXldwsUn1wPkB5U77OMc12XKchDkSdtcpwTv26n-3dQqJW9zoYc2cwQNSjTockhAwJZjJkihUE7xdBRUoB2VzBA76zWpJBZ8yA-X_E5N9E:1wWypI:eDmPvBPk0nhNrWT7obOZF-UzhL-_8zq6I7P9JmqPhLI', '2026-06-09 16:00:16.934325'),
('pmxh2ec3t5druinedfwvt2mo3mgn9pif', '.eJxVjDsOwjAQBe_iGln-O1DS5wzWeneNA8iR4qRC3B0ipYD2zcx7iQTbWtPWeUkTiYsw4vS7ZcAHtx3QHdptlji3dZmy3BV50C7Hmfh5Pdy_gwq9fuuzJSAEEzUadmQ5I3v0CCEPmF3wFgrr6NCrCOwQHBZrBlWC0pkiiPcHHdQ5Nw:1wQ8M2:cdvpJY7DQbG8Np5Orxp7GOKftcVBa6I32xXG-fuiJp0', '2026-06-04 18:42:46.910135'),
('swn9xsdqdmfu4fdoogkuydq54jcjqpna', '.eJxVjEEOwiAQRe_C2hAKQwGX7j0DYWBGqoYmpV0Z765NutDtf-_9l4hpW2vcOi1xKuIsvDj9bpjyg9oOyj212yzz3NZlQrkr8qBdXudCz8vh_h3U1Ou3dsTKap2MGpkJteHgPBMDFqNDtsYFtjYrDd4MqgTlccQyEDjtwQOI9wfocjda:1wUPcS:pKcKpwspJy2VI5qFDompcbKKBvxPNRKb9l4F-60n0Gk', '2026-06-16 13:57:24.844030'),
('ugtbv7k4ka7phhdgfe7m3euv8nc0o14o', '.eJxVjEEOgjAQRe_StWmGwSmtS_ecgcx0wKKmTSisjHdXEha6_e-9_zIDb2satjouw6zmYhpz-t2E42PMO9A751uxseR1mcXuij1otX3R8Xk93L-DxDV9a3DiMbI2ET1wK24iAN8idUEFfIfcUZAwYUuIoORU6MyNUCAg1GDeH8YjNtM:1wBHyY:Y-veoAS-nwoHP6SswfcCIaHxOWkGmA40PbEkjpiGOos', '2026-04-24 19:57:10.553060'),
('ui76rr9lw1s8xcibyo8bltmanlapletl', '.eJxVjDsOwjAQBe_iGln-O1DS5wzWeneNA8iR4qRC3B0ipYD2zcx7iQTbWtPWeUkTiYsw4vS7ZcAHtx3QHdptlji3dZmy3BV50C7Hmfh5Pdy_gwq9fuuzJSAEEzUadmQ5I3v0CCEPmF3wFgrr6NCrCOwQHBZrBlWC0pkiiPcHHdQ5Nw:1wQB2T:2aw0yHJ3NSVbBxTDKUdaSPPDWgiJ_CyDnEwlvHaEomA', '2026-06-04 21:34:45.195750'),
('x852kz4fxqtwo5u88slf89cwao07zx4z', 'e30:1wHO5b:r75QjRv8L5VG7cmAYjszuXrLCLmXYLQVaKtgifZaJyw', '2026-05-11 15:41:39.441919'),
('xmde8oxfsdmlnighgsxb8tf7iafy1gdx', '.eJxVjDkOwjAURO_iGlnBuynpOYP1FxsHkCPFSYW4O4mUArrRvDfzFgnWpaa15zmNLC5CidNvh0DP3HbAD2j3SdLUlnlEuSvyoF3eJs6v6-H-HVTodVsDs9cKjI2emXQsGIuLmIGdAtiyJjZDdE4pMhQpDDb4s7EFiw4ITny-BmQ4eg:1wY6ky:PxufyNIiZBiPdV_hbWxsrxj495Su2ndjexzxG1BEXes', '2026-06-26 18:37:28.352224'),
('xxgjayo5ir6jjqvolgpuss6duj11uw0j', 'e30:1wHO5V:NFdlh_ywhhQvZ39kttdSZCu5vGRJOiuW56VZHICVJ4I', '2026-05-11 15:41:33.200684'),
('y9g95o5bc4z65w70qapb4m7no5wctmqs', '.eJxVjEEOwiAQAP_C2RCgSMGj976BLLuLVA0kpT0Z_25qetDrzGReIsK2lrh1XuJM4iK0EqdfmAAfXHdDd6i3JrHVdZmT3BN52C6nRvy8Hu3foEAv368nZ0MmNko7pQ1645H4HJKjnGBEhBwG9ooBrTeGRhxctp4Nae20eH8AD004Xw:1wYFqj:nV-IhU8_gi1rhqRBQm9_Esy7uKyxX2AdU7fDw4kkd_k', '2026-06-27 04:20:01.424411');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `website_record`
--

CREATE TABLE `website_record` (
  `id` bigint(20) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `phone` varchar(15) NOT NULL,
  `address` varchar(100) NOT NULL,
  `city` varchar(50) NOT NULL,
  `state` varchar(50) NOT NULL,
  `zip_code` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `website_record`
--

INSERT INTO `website_record` (`id`, `created_at`, `first_name`, `last_name`, `email`, `phone`, `address`, `city`, `state`, `zip_code`) VALUES
(3, '2026-05-15 22:04:07.969549', 'melina', 'castro', 'castro@gmail.com', '124132412', 'sena cll34', 'medellin', 'antioquia', '50001'),
(5, '2026-05-16 09:00:00.000000', 'Juan', 'Perez', 'juan.perez@email.com', '3001112233', 'Calle 10 # 45-20', 'Medellín', 'Antioquia', '050001'),
(6, '2026-05-16 10:30:00.000000', 'Ana', 'Gomez', 'ana.gomez@email.com', '3004445566', 'Carrera 70 # 30-10', 'Medellín', 'Antioquia', '050002'),
(7, '2026-05-17 08:15:00.000000', 'Carlos', 'Ruiz', 'carlos.ruiz@email.com', '3107778899', 'Transversal 39B', 'Medellín', 'Antioquia', '050010'),
(8, '2026-05-17 14:20:00.000000', 'Laura', 'Torres', 'laura.torres@email.com', '3201112233', 'Av. Nutibara 50-10', 'Medellín', 'Antioquia', '050011'),
(9, '2026-05-18 09:45:00.000000', 'Pedro', 'Lopez', 'pedro.lopez@email.com', '3156667788', 'Calle 50 # 40-30', 'Medellín', 'Antioquia', '050012'),
(10, '2026-05-18 11:00:00.000000', 'Sofia', 'Diaz', 'sofia.diaz@email.com', '3189990011', 'Carrera 45 # 50-20', 'Medellín', 'Antioquia', '050013'),
(11, '2026-05-19 16:10:00.000000', 'Diego', 'Martinez', 'diego.m@email.com', '3012223344', 'Calle 100 # 20-10', 'Medellín', 'Antioquia', '050014'),
(12, '2026-05-19 17:30:00.000000', 'Valentina', 'Rios', 'vale.rios@email.com', '3124445566', 'Carrera 80 # 45-30', 'Medellín', 'Antioquia', '050015'),
(13, '2026-05-20 08:00:00.000000', 'Andres', 'Castillo', 'andres.c@email.com', '3137778899', 'Calle 33 # 60-40', 'Medellín', 'Antioquia', '050016'),
(15, '2026-05-21 09:20:00.000000', 'Felipe', 'Morales', 'felipe.m@email.com', '3009998877', 'Calle 55 # 30-20', 'Medellín', 'Antioquia', '050018'),
(20, '2026-05-23 16:20:00.000000', 'Isabella', 'Zapata', 'isabella.z@email.com', '3144445566', 'Carrera 70 # 80-40', 'Medellín', 'Antioquia', '050023'),
(25, '2026-06-02 12:48:19.636344', 'MARIANA', 'CAMILA', 'CAMILA@GMAIL.COM', '324235', 'CLL34', 'medellin', 'antioquia', '50001');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `auth_group`
--
ALTER TABLE `auth_group`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Indices de la tabla `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  ADD KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`);

--
-- Indices de la tabla `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`);

--
-- Indices de la tabla `auth_user`
--
ALTER TABLE `auth_user`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Indices de la tabla `auth_user_groups`
--
ALTER TABLE `auth_user_groups`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  ADD KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`);

--
-- Indices de la tabla `auth_user_user_permissions`
--
ALTER TABLE `auth_user_user_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  ADD KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`);

--
-- Indices de la tabla `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD PRIMARY KEY (`id`),
  ADD KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  ADD KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`);

--
-- Indices de la tabla `django_content_type`
--
ALTER TABLE `django_content_type`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`);

--
-- Indices de la tabla `django_migrations`
--
ALTER TABLE `django_migrations`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `django_session`
--
ALTER TABLE `django_session`
  ADD PRIMARY KEY (`session_key`),
  ADD KEY `django_session_expire_date_a5c62663` (`expire_date`);

--
-- Indices de la tabla `website_record`
--
ALTER TABLE `website_record`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `auth_group`
--
ALTER TABLE `auth_group`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `auth_permission`
--
ALTER TABLE `auth_permission`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=29;

--
-- AUTO_INCREMENT de la tabla `auth_user`
--
ALTER TABLE `auth_user`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT de la tabla `auth_user_groups`
--
ALTER TABLE `auth_user_groups`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `auth_user_user_permissions`
--
ALTER TABLE `auth_user_user_permissions`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `django_admin_log`
--
ALTER TABLE `django_admin_log`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- AUTO_INCREMENT de la tabla `django_content_type`
--
ALTER TABLE `django_content_type`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT de la tabla `django_migrations`
--
ALTER TABLE `django_migrations`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20;

--
-- AUTO_INCREMENT de la tabla `website_record`
--
ALTER TABLE `website_record`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=28;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  ADD CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`);

--
-- Filtros para la tabla `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`);

--
-- Filtros para la tabla `auth_user_groups`
--
ALTER TABLE `auth_user_groups`
  ADD CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  ADD CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

--
-- Filtros para la tabla `auth_user_user_permissions`
--
ALTER TABLE `auth_user_user_permissions`
  ADD CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  ADD CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

--
-- Filtros para la tabla `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  ADD CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
COMMIT;


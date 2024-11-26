# RK322XH Release Note

## rk322xh_ddr_{333,400}MHz_v1.21.bin

| Date       | File                               | Build commit | Severity |
| ---------- | ---------------------------------- | ------------ | -------- |
| 2024-11-26 | rk322xh_ddr_{333,400}MHz_v1.21.bin | 48fb7bc      | moderate |

### Fixed

| Index | Severity | Update                           | Issue description | Issue source |
| ----- | -------- | -------------------------------- | ----------------- | ------------ |
| 1     | moderate | Modify the version print format. | -                 | -            |

------

## rk322xh_ddr_{333,400}MHz_v1.20.bin

| Date       | File                               | Build commit | Severity |
| ---------- | ---------------------------------- | ------------ | -------- |
| 2024-10-18 | rk322xh_ddr_{333,400}MHz_v1.20.bin | 4d28874      | moderate |

### Fixed

| Index | Severity | Update                                                 | Issue description                                            | Issue source |
| ----- | -------- | ------------------------------------------------------ | ------------------------------------------------------------ | ------------ |
| 1     | moderate | Fix low probability DDR4 capacity detection anomalies. | Occasionally, there may be a mismatch in DDR4 capacity by 1/2 or 1/4 when the device is powered on or off. | -            |

------

## rk322xh_bl32_v2.02.bin

| Date       | File                   | Build commit | Severity |
| ---------- | :--------------------- | ------------ | -------- |
| 2023-08-14 | rk322xh_bl32_v2.02.bin | 44e25f04     | critical |

### Fixed

| Index | Severity  | Update                        | Issue description                                            | Issue source |
| ----- | --------- | ----------------------------- | ------------------------------------------------------------ | ------------ |
| 1     | critical  | Fix security vulnerabilities. | Hackers can exploit vulnerabilities to attack OPTEE OS.      |              |
| 2     | important | Fix memory leaks.             | Customer calls TEE_ DerivekeyFromHard may experience memory leakage issues. | 374096       |

------


# RV1103B Release Note

## rv1103b_tee_ta_v1.02.bin

| Date       | File                     | Build commit | Severity  |
| ---------- | :----------------------- | ------------ | --------- |
| 2024-11-01 | rv1103b_tee_ta_v1.02.bin | 9f2aca7d1    | important |

### Fixed

| Index | Severity  | Update                                                       | Issue description                                            | Issue source |
| ----- | --------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------ |
| 1     | important | check whether the rpmb key has been burned before changing security level | upgrading from weak security level to strong security level may result in rpmb key verification failure | -            |
| 2     | important | fixed RSA OAEP MGF1 algorithm                                | TA will report an error when using RSA algorithm OAEP MGF1 padding method | -            |

------

## rv1103b_hpmcu_wrap_v2.02.bin

| Date       | File                         | Build commit     | Severity  |
| ---------- | :--------------------------- | ---------------- | --------- |
| 2024-10-22 | rv1103b_hpmcu_wrap_v2.02.bin | rockit_ko:26f0ca4 | important |

### New

1. Support double channel wrap.

------

## rv1103b_ddr_924MHz{_tb}_v1.05.bin

| Date       | File                              | Build commit | Severity  |
| ---------- | :-------------------------------- | ------------ | --------- |
| 2024-10-14 | rv1103b_ddr_924MHz{_tb}_v1.05.bin | a0d2414c29   | important |

### Fixed

| Index | Severity  | Update                                          | Issue description | Issue source |
| ----- | --------- | ----------------------------------------------- | ----------------- | ------------ |
| 1     | important | Fix DDR3 924MHz probabilistic resume hang issue | -                 | -            |

------

## rv1103b_tee_ta_v1.01.bin

| Date       | File                     | Build commit | Severity  |
| ---------- | :----------------------- | ------------ | --------- |
| 2024-10-14 | rv1103b_tee_ta_v1.01.bin | 066b2fbeb    | important |

### New

1. Modify the TEE loading address to 62M.

------


## rv1103b_flash_acc_w25n01xx_v1.00.bin

| Date       | File                              | Build commit | Severity  |
| ---------- | :--------------------------------------- | ----------- | -------- |
| 2024-10-08 | rv1103b_flash_acc_w25n01xx_v1.00.bin        | c2c14bb7e419  | important     |

### New

1. Add w25n01jw rom accelerator.

------

## rv1103b_usbplug_auto_merge_v1.10.bin

| Date       | File                               | Build commit                                   | Severity |
| ---------- | :--------------------------------- | ---------------------------------------------- | -------- |
| 2024-09-29 | rv1103b_usbplug_auto_merge_v1.10.bin | f9ecba2b | moderate |

### New

1. Change cs1 to gpio2a6.

------

## rv1103b_usbplug_auto_merge_v1.00.bin

| Date       | File                               | Build commit                                   | Severity |
| ---------- | :--------------------------------- | ---------------------------------------------- | -------- |
| 2024-09-25 | rv1103b_usbplug_auto_merge_v1.00.bin | a87eca5 | moderate |

### New

1. Initial version.

------

## rv1103b_ddr_924MHz{_tb}_v1.04.bin

| Date       | File                              | Build commit | Severity  |
| ---------- | :-------------------------------- | ------------ | --------- |
| 2024-08-30 | rv1103b_ddr_924MHz{_tb}_v1.04.bin | ccb664bdcf   | important |

### New

1. Improve DDR stability.

------

## rv1103b_ddr_924MHz{_tb}_v1.03.bin

| Date       | File                              | Build commit | Severity  |
| ---------- | :-------------------------------- | ------------ | --------- |
| 2024-08-26 | rv1103b_ddr_924MHz{_tb}_v1.03.bin | b991ae72ff   | important |

### Fixed

| Index | Severity  | Update                                   | Issue description | Issue source |
| ----- | --------- | ---------------------------------------- | ----------------- | ------------ |
| 1     | important | Fix gate training timeout of DDR2 528MHz | -                 | -            |
| 2     | important | Fix isp mipi drop when 4M 60fps          | -                 | -            |
| 3     | important | Fix DDR setting for power-saving         | -                 | -            |

------

## rv1103b_tee_ta_v1.00.bin

| Date       | File                     | Build commit | Severity  |
| ---------- | :----------------------- | ------------ | --------- |
| 2024-08-20 | rv1103b_tee_ta_v1.00.bin | ed4478bc9    | important |

### New

1. Add OPTEE support.

------

## rv1103b_{ddr,spl,usbplug,hpmcu}_v1.00.bin

| Date       | File                               | Build commit                                   | Severity |
| ---------- | :--------------------------------- | ---------------------------------------------- | -------- |
| 2024-07-29 | rv1103b_{ddr,spl,usbplug,hpmcu}_v1.00.bin | ddr:1b742cd9d6#spl:3687236ab1c:usbplug:c53c564#rtt:3143c22c#hal:939ec3d5#battery_ipc:06ccc158 | moderate |

### New

1. Initial version.

------


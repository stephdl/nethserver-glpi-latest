Name: nethserver-glpi-latest
Version: 1.0.10
Release: 1%{?dist}
Summary: Configure glpi
Source: %{name}-%{version}.tar.gz
BuildArch: noarch
URL: %{url_prefix}/%{name}
License: GPL
%define glpi_version 9.5.12
%define glpi_name glpi
Source1: https://github.com/glpi-project/glpi/releases/download/%{glpi_version}/%{glpi_name}-%{glpi_version}.tgz 
Source2: glpi-local_define.php
Source3: glpi-downstream.php
Source4: glpi-logrotate

BuildRequires: nethserver-devtools

Requires: nethserver-httpd
Conflicts: glpi
Requires: nethserver-rh-php73-php-fpm
Requires: sclo-php73-php-sodium rh-php73-php-xmlrpc libsodium
Requires: nethserver-rh-mariadb105 rh-mariadb105-mariadb-server-utils
%description
Install and configure a glpi instance on NethServer
GLPI is the Information Resource-Manager with an additional Administration-
Interface. You can use it to build up a database with an inventory for your 
company (computer, software, printers...). It has enhanced functions to make
the daily life for the administrators easier, like a job-tracking-system with
mail-notification and methods to build a database with basic information 
about your network-topology.

%prep

%setup

%build
%{makedocs}
perl createlinks
mkdir -p root/etc/e-smith/templates/etc/glpi/config_db.php
ln -s /etc/e-smith/templates-default/template-begin-php root/etc/e-smith/templates/etc/glpi/config_db.php/template-begin
sed -i 's/_RELEASE_/%{version}/' %{name}.json

%install
rm -rf %{buildroot}
(cd root   ; find . -depth -print | cpio -dump %{buildroot})

# set specific settings
mkdir -p %{buildroot}/etc/%{glpi_name}
cp  %SOURCE2 %{buildroot}/etc/%{glpi_name}/local_define.php

# configuration file path
mkdir -p %{buildroot}/usr/share/%{glpi_name}/inc
cp  %SOURCE3 %{buildroot}/usr/share/glpi/inc/downstream.php

# Log rotate
mkdir -p %{buildroot}%{_sysconfdir}/logrotate.d
cp -pr %SOURCE4 %{buildroot}%{_sysconfdir}/logrotate.d/glpi

# move all files to /usr/share/glpi
mkdir -p  %{buildroot}%{_datadir}/%{glpi_name}
tar xzvf %{SOURCE1} -C %{buildroot}/usr/share

# ===== files =====

mkdir -p %{buildroot}/%{_localstatedir}/lib/%{glpi_name}
mv %{buildroot}/usr/share/%{glpi_name}/files/* %{buildroot}/%{_localstatedir}/lib/%{glpi_name}

# ===== log =====
mkdir -p %{buildroot}%{_localstatedir}/log
mv %{buildroot}/%{_localstatedir}/lib/%{glpi_name}/_log %{buildroot}%{_localstatedir}/log/%{glpi_name}


# clean up
find %{buildroot} -name remove.txt -exec rm -f {} \; -print
rm -f %{buildroot}%{_datadir}/%{glpi_name}/install/install.php

mkdir -p %{buildroot}/usr/share/cockpit/%{name}/
mkdir -p %{buildroot}/usr/share/cockpit/nethserver/applications/
mkdir -p %{buildroot}/usr/libexec/nethserver/api/%{name}/
cp -a manifest.json %{buildroot}/usr/share/cockpit/%{name}/
cp -a logo.png %{buildroot}/usr/share/cockpit/%{name}/
cp -a %{name}.json %{buildroot}/usr/share/cockpit/nethserver/applications/
cp -a api/* %{buildroot}/usr/libexec/nethserver/api/%{name}/

mkdir -p %{buildroot}/var/opt/rh/rh-mariadb105/lib/mysql-glpi

%{genfilelist} %{buildroot} \
    --dir /var/log/glpi 'attr(2770,apache,apache)' \
    --dir /var/lib/glpi 'attr(2770,apache,apache)' \
    --dir /var/lib/glpi/_cache 'attr(2770,apache,apache)' \
    --dir /var/lib/glpi/_cron 'attr(2770,apache,apache)' \
    --dir /var/lib/glpi/_dumps 'attr(2770,apache,apache)' \
    --dir /var/lib/glpi/_graphs 'attr(2770,apache,apache)' \
    --dir /var/lib/glpi/_locales 'attr(2770,apache,apache)' \
    --dir /var/lib/glpi/_lock 'attr(2770,apache,apache)' \
    --dir /var/lib/glpi/_pictures 'attr(2770,apache,apache)' \
    --dir /var/lib/glpi/_plugins 'attr(2770,apache,apache)' \
    --dir /var/lib/glpi/_rss 'attr(2770,apache,apache)' \
    --dir /var/lib/glpi/_sessions 'attr(2770,apache,apache)' \
    --dir /var/lib/glpi/_tmp 'attr(2770,apache,apache)' \
    --dir /var/lib/glpi/_uploads 'attr(2770,apache,apache)' \
    --dir /var/opt/rh/rh-mariadb105/lib/mysql-glpi 'attr(0755,mysql,mysql)'  | grep -v -e '/usr/share/glpi'\
     > %{name}-%{version}-filelist

%files -f %{name}-%{version}-filelist
%defattr(-,root,root)
%doc COPYING
%dir %{_nseventsdir}/%{name}-update
%attr(0440,root,root) /etc/sudoers.d/50_nsapi_nethserver_glpi
%dir %attr(0755,mysql,mysql) /var/opt/rh/rh-mariadb105/lib/mysql-glpi
%{_datadir}/%{glpi_name}
%config(noreplace) %{_sysconfdir}/logrotate.d/glpi
%dir %attr(2770,apache,apache) %{_sysconfdir}/%{glpi_name}
%config(noreplace) %{_sysconfdir}/%{glpi_name}/local_define.php
%dir %attr(0750,apache,apache) %{_datadir}/%{glpi_name}/config
%dir %attr(0750,apache,apache) %{_datadir}/%{glpi_name}/marketplace
%dir %attr(0750,apache,apache) %{_datadir}/%{glpi_name}/plugins
# This folder can contain private information (sessions, docs, ...)
%attr(2770,apache,apache) %{_localstatedir}/lib/%{glpi_name}/*
%attr(2770,apache,apache) %dir %{_localstatedir}/log/%{glpi_name}

%postun
if [ $1 == 0 ] ; then
    /usr/bin/rm -f /etc/httpd/conf.d/glpi.conf
    /usr/bin/systemctl reload httpd
fi

%changelog
* Wed Apr 05 2023 Stephane de Labrusse <stephdl@de-labrusse.fr> - 1.0.10-1
- go to 9.5.12 

* Wed Apr 05 2023 Stephane de Labrusse <stephdl@de-labrusse.fr> - 1.0.9-1

* wed april 5 2023 stephane de Labrusse <stephdl@de-labrusse.fr> 1.0.9
- go to 9.5.12

* Tue Aug 16 2022 stephane de Labrusse <stephdl@de-labrusse.fr> 1.0.8
- allow apache in /usr/share/glpi/plugins

* Mon Aug 8 2022 stephane de Labrusse <stephdl@de-labrusse.fr> 1.0.7
- go to 9.5.8

* Wed Feb 2 2022 stephane de Labrusse <stephdl@de-labrusse.fr> 1.0.6
- Populate the timezone
* Tue Feb 1 2022 stephane de Labrusse <stephdl@de-labrusse.fr> 1.0.4
- allow user glpi to mysql.time_zone_name
* Mon Jan 31 2022 stephane de Labrusse <stephdl@de-labrusse.fr> 1.0.3
- Migrate old files path to newer path location
* Fri Jan 28 2022 stephane de Labrusse <stephdl@de-labrusse.fr> 1.0.2
- Migrate old DB from glpi version 0.90
- Bump to 9.5.7
* Tue Sep 21 2021 stephane de Labrusse <stephdl@de-labrusse.fr> 1.0.1
- Bump to 9.5.6
* Wed Aug 25 2021 stephane de Labrusse <stephdl@de-labrusse.fr> 1.0.0
- First release to NS7 with glpi 9.5.5

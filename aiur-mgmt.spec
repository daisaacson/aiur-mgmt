Name: aiur-mgmt
Version: 0.4.4
Release: 1%{?dist}
Summary: Aiur Management

Group: Applications/System
License: GPLv3
URL: https://raw.githubusercontent.com/daisaacson/aiur-mgmt/aiur-mgmt
Source0: https://raw.githubusercontent.com/daisaacson/aiur-mgmt/%{name}/%{name}-%{version}.tar.gz

#BuildRequires:	
Requires: python

%description
Aiur Managment - A collection of scripts and commands


%prep
%setup -q


%build


%install
rm -rf $RPM_BUILD_ROOT
install -m 0755 -d $RPM_BUILD_ROOT%{_bindir}
install -pm 0755 apatch.sh $RPM_BUILD_ROOT%{_bindir}/ayum
install -pm 0755 b64.py $RPM_BUILD_ROOT%{_bindir}/ab64
install -pm 0755 forced-commands.sh $RPM_BUILD_ROOT%{_bindir}/forced-commands
install -pm 0755 sslComponent.py $RPM_BUILD_ROOT%{_bindir}/assl
install -pm 0755 dnssearch.py $RPM_BUILD_ROOT%{_bindir}/dnssearch
install -pm 0755 modem-status.py $RPM_BUILD_ROOT%{_bindir}/modem-status
install -pm 0755 mping.sh $RPM_BUILD_ROOT%{_bindir}/mping


%files
%defattr(-,root,root)
%attr(0755,root,root) %{_bindir}/*


%changelog
* Tue Oct 27 2015 daisaacson <49328302+daisaacson@users.noreply.github.com> - 0.4.4-1
- Added mping script
* Sat Sep 5 2015 daisaacson <49328302+daisaacson@users.noreply.github.com> - 0.4.3-1
- dnssearch updates
* Fri Jul 10 2015 daisaacson <49328302+daisaacson@users.noreply.github.com> - 0.4.2-1
- Improvments to ayum
* Sun Mar 22 2015 daisaacson <49328302+daisaacson@users.noreply.github.com> - 0.4.1-1
- Cleaned up dnssearch output
* Sat Mar 21 2015 daisaacson <49328302+daisaacson@users.noreply.github.com> - 0.4-1
- Added dnssearch script
* Mon Jan 5 2015 daisaacson <49328302+daisaacson@users.noreply.github.com> - 0.3-1
- Improvements to ayum
* Wed Sep 24 2014 daisaacson <49328302+daisaacson@users.noreply.github.com> - 0.2-1
- Uncomment reboot on patch.sh
* Fri Sep 5 2014 daisaacson <49328302+daisaacson@users.noreply.github.com> - 0.1-1
- Initial build

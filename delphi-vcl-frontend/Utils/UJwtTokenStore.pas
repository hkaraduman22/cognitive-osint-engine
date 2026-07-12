unit UJwtTokenStore;

interface

type
  TJwtTokenStore = class
  private
    class var FToken: string;
    class var FRefreshToken: string;
    class var FUsername: string;
  public
    class procedure SetToken(const AToken: string); static;
    class function GetToken: string; static;
    class function HasToken: Boolean; static;
    class procedure Clear; static;

    class procedure SetRefreshToken(const AToken: string); static;
    class function GetRefreshToken: string; static;
    class procedure SetUsername(const AUsername: string); static;
    class function GetUsername: string; static;

    /// <summary>Kullanici adi + refresh token'i DPAPI ile sifreleyip diske yazar
    /// (uygulama yeniden acildiginda kullanilir).</summary>
    class procedure PersistSession; static;
    /// <summary>Diskte kayitli bir oturum varsa okuyup belleğe yukler. Bulundu/bulunmadi doner.</summary>
    class function TryLoadPersistedSession: Boolean; static;
    /// <summary>Kalici oturum dosyasini siler (logout sirasinda cagrilir).</summary>
    class procedure ClearPersistedSession; static;
  end;

implementation

uses
  System.SysUtils,
  USecureStorage;

class procedure TJwtTokenStore.Clear;
begin
  FToken := '';
  FRefreshToken := '';
  FUsername := '';
end;

class function TJwtTokenStore.GetToken: string;
begin
  Result := FToken;
end;

class function TJwtTokenStore.HasToken: Boolean;
begin
  Result := FToken <> '';
end;

class procedure TJwtTokenStore.SetToken(const AToken: string);
begin
  FToken := Trim(AToken);
end;

class procedure TJwtTokenStore.SetRefreshToken(const AToken: string);
begin
  FRefreshToken := Trim(AToken);
end;

class function TJwtTokenStore.GetRefreshToken: string;
begin
  Result := FRefreshToken;
end;

class procedure TJwtTokenStore.SetUsername(const AUsername: string);
begin
  FUsername := Trim(AUsername);
end;

class function TJwtTokenStore.GetUsername: string;
begin
  Result := FUsername;
end;

class procedure TJwtTokenStore.PersistSession;
begin
  TSecureStorage.SaveSession(FUsername, FRefreshToken);
end;

class function TJwtTokenStore.TryLoadPersistedSession: Boolean;
var
  LUsername, LRefreshToken: string;
begin
  Result := TSecureStorage.LoadSession(LUsername, LRefreshToken);
  if Result then
  begin
    FUsername := LUsername;
    FRefreshToken := LRefreshToken;
  end;
end;

class procedure TJwtTokenStore.ClearPersistedSession;
begin
  TSecureStorage.ClearSession;
end;

end.

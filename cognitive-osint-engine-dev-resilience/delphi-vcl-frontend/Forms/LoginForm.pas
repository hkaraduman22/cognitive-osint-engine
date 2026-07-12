unit LoginForm;

interface

uses
  Winapi.Windows,
  Winapi.Messages,
  System.SysUtils,
  System.Variants,
  System.Classes,
  System.JSON,
  System.Net.HttpClient,
  Vcl.Graphics,
  Vcl.Controls,
  Vcl.Forms,
  Vcl.Dialogs,
  Vcl.StdCtrls;

type
  TFrmLogin = class(TForm)
    LblTitle: TLabel;
    LblUsername: TLabel;
    LblPassword: TLabel;
    EdtUsername: TEdit;
    EdtPassword: TEdit;
    BtnLogin: TButton;
    BtnOpenRegister: TButton;
    LblStatus: TLabel;
    procedure BtnLoginClick(Sender: TObject);
    procedure BtnOpenRegisterClick(Sender: TObject);
  private
    procedure SetBusy(const AValue: Boolean);
  public
    { Public declarations }
  end;

var
  FrmLogin: TFrmLogin;

implementation

{$R *.dfm}

uses
  UAuthService,
  UHttpApiClient,
  UJwtTokenStore,
  RegisterForm,
  AdminForm,
  MainForm;

procedure TFrmLogin.BtnLoginClick(Sender: TObject);
var
  LAuthService: TAuthService;
  LClient: THttpApiClient;
  LResponse: IHTTPResponse;
  LJsonValue: TJSONValue;
  LJsonObj: TJSONObject;
  LIsAdminValue: TJSONValue;
  LToken: string;
  LIsAdmin: Boolean;
begin
  SetBusy(True);
  try
    LblStatus.Caption := 'Giris yapiliyor...';
    LAuthService := TAuthService.Create;
    try
      LToken := LAuthService.Login(Trim(EdtUsername.Text), EdtPassword.Text);
      TJwtTokenStore.SetToken(LToken);
    finally
      LAuthService.Free;
    end;

    LClient := THttpApiClient.Create;
    try
      LResponse := LClient.Get('/auth/me', TJwtTokenStore.GetToken);
      if LResponse.StatusCode <> 200 then
        raise Exception.CreateFmt('/auth/me basarisiz. HTTP %d', [LResponse.StatusCode]);

      LJsonValue := TJSONObject.ParseJSONValue(LResponse.ContentAsString(TEncoding.UTF8));
      try
        if not (LJsonValue is TJSONObject) then
          raise Exception.Create('/auth/me yaniti gecersiz.');

        LJsonObj := TJSONObject(LJsonValue);
        LIsAdminValue := LJsonObj.GetValue('is_admin');
        if not Assigned(LIsAdminValue) then
          raise Exception.Create('/auth/me is_admin alani bulunamadi.');

        if LIsAdminValue is TJSONBool then
          LIsAdmin := TJSONBool(LIsAdminValue).AsBoolean
        else
          LIsAdmin := SameText(Trim(LIsAdminValue.Value), 'true') or (Trim(LIsAdminValue.Value) = '1');
      finally
        LJsonValue.Free;
      end;
    finally
      LClient.Free;
    end;

    LblStatus.Caption := 'Giris basarili. JWT kaydedildi.';

    if LIsAdmin then
      with TFrmAdmin.Create(Self) do
      try
        ShowModal;
      finally
        Free;
      end
    else
    begin
      if not Assigned(FrmMain) then
        Application.CreateForm(TFrmMain, FrmMain);

      FrmMain.SetSessionUser(Trim(EdtUsername.Text));
      FrmMain.Show;
    end;

    Hide;
  except
    on E: Exception do
      LblStatus.Caption := E.Message;
  end;
  SetBusy(False);
end;

procedure TFrmLogin.BtnOpenRegisterClick(Sender: TObject);
begin
  with TFrmRegister.Create(Self) do
  try
    if ShowModal = mrOk then
      LblStatus.Caption := 'Kayit tamamlandi. Giris aktif.';
  finally
    Free;
  end;
end;

procedure TFrmLogin.SetBusy(const AValue: Boolean);
begin
  BtnLogin.Enabled := not AValue;
  BtnOpenRegister.Enabled := not AValue;
  EdtUsername.Enabled := not AValue;
  EdtPassword.Enabled := not AValue;
end;

end.
